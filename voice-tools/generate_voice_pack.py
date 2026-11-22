#!/usr/bin/env python3
"""Pré-grava falas genéricas pelo Chatterbox local, sem dependências externas.

Sem --voice ou --reference, apenas --probe/--dry-run podem ser usados.
Este programa nunca inicia, reconfigura ou instala o servidor TTS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
PARAMETERS = {
    "output_format": "wav", "language": "pt", "temperature": 0.7,
    "exaggeration": 0.95, "cfg_weight": 0.5, "seed": 4096,
    "speed_factor": 1.0, "split_text": False, "chunk_size": 120,
    "stream": False,
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def basename(value):
    if not value or value in (".", "..") or "/" in value or "\\" in value or ":" in value:
        raise argparse.ArgumentTypeError("Informe somente o nome do áudio existente no servidor, sem caminho.")
    return value


def read_json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name + ".", suffix=".tmp", delete=False) as stream:
            name = stream.name
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def atomic_json(path, value):
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def request(server, endpoint, timeout, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(server.rstrip("/") + endpoint, data=data,
                  headers={"Accept": "application/json" if payload is None else "audio/wav",
                           "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return response.read()
    except HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} em {endpoint}: {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Falha ou timeout em {endpoint}: {exc}") from exc


def get_json(server, endpoint, timeout):
    try:
        return json.loads(request(server, endpoint, timeout))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Resposta JSON inválida em {endpoint}.") from exc


def probe(server, timeout):
    result = {"server": server, "checked_at": utc_now(), "endpoints": {}}
    for endpoint in ("/get_predefined_voices", "/get_reference_files", "/api/model-info"):
        try:
            result["endpoints"][endpoint] = {"status": "ok", "response": get_json(server, endpoint, timeout)}
        except (RuntimeError, ValueError) as exc:
            result["endpoints"][endpoint] = {"status": "unavailable", "error": str(exc)}
    # A resposta é preservada; um timeout em model-info não demonstra modelo ativo.
    return result


def flatten_lines(lines):
    required = ("welcome", "entry", "activities", "success", "retry", "complete", "hints", "finale")
    if not isinstance(lines, dict) or any(k not in lines for k in required):
        raise ValueError("lines.json deve conter welcome, entry, activities, success, retry e complete.")
    rows = []
    for key in required:
        value = lines[key]
        items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else [(None, value)]
        for subkey, text in items:
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Texto inválido em {key}.{subkey}.")
            clip = key if subkey is None else f"{key}.{subkey}"
            if not all(c.isalnum() or c in "._-" for c in clip):
                raise ValueError(f"Identificador de clipe inválido: {clip}")
            rows.append((clip, text))
    return rows


def payload_for(text, voice=None, reference=None):
    payload = {"text": text, **PARAMETERS}
    if voice:
        payload.update(voice_mode="predefined", predefined_voice_id=voice)
    elif reference:
        payload.update(voice_mode="clone", reference_audio_filename=reference)
    return payload


def transform_for(semitones):
    return {"pitch_semitones": semitones, "pitch_ratio": 2 ** (semitones / 12),
            "engine": "ffmpeg-rubberband" if semitones else "none", "tempo": 1.0,
            "formant": "preserved", "pitchq": "quality", "output_codec": "pcm_s16le" if semitones else "unchanged",
            "projection": {"profile": "authoritative-warm-v1",
                           "equalizer": {"f": 180, "t": "q", "w": 1, "g": 1.5},
                           "compressor": {"threshold": 0.12, "ratio": 2.2, "attack": 8, "release": 100, "makeup": 1.3},
                           "limiter": {"limit": 0.94, "level": "disabled"}} if semitones else None}


def digest(payload, transform=None):
    identity = payload if transform is None else {"tts": payload, "postprocess": transform}
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def finalize_pipe_wav(data):
    """FFmpeg em pipe usa tamanhos 0xffffffff; fixa-os após a captura completa."""
    if len(data) < 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("FFmpeg não retornou RIFF/WAVE.")
    result = bytearray(data)
    struct.pack_into("<I", result, 4, len(result) - 8)
    offset = 12
    while offset + 8 <= len(result):
        size = struct.unpack_from("<I", result, offset + 4)[0]
        if result[offset:offset + 4] == b"data" and size == 0xFFFFFFFF:
            struct.pack_into("<I", result, offset + 4, len(result) - offset - 8)
            break
        if offset + 8 + size > len(result):
            raise ValueError("Saída WAV do FFmpeg truncada.")
        offset += 8 + size + (size % 2)
    return bytes(result)


def apply_pitch(data, transform, ffmpeg, timeout):
    if not transform["pitch_semitones"]:
        return data
    ratio = format(transform["pitch_ratio"], ".12g")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
               "-af", f"rubberband=tempo=1:pitch={ratio}:formant=preserved:pitchq=quality,equalizer=f=180:t=q:w=1:g=1.5,acompressor=threshold=.12:ratio=2.2:attack=8:release=100:makeup=1.3,alimiter=limit=.94:level=disabled",
               "-c:a", "pcm_s16le", "-f", "wav", "pipe:1"]
    try:
        process = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Falha no pós-processamento de voz: {exc}") from exc
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace")[-2500:]
        raise RuntimeError(f"FFmpeg falhou (código {process.returncode}): {detail}")
    result = finalize_pipe_wav(process.stdout)
    validate_wav(result)
    return result


def validate_wav(data):
    """Confere RIFF/WAVE e chunks, aceitando PCM e WAV float sem transcodificar."""
    if len(data) < 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("A resposta não é um arquivo RIFF/WAVE válido; nenhum áudio foi salvo.")
    declared = struct.unpack_from("<I", data, 4)[0] + 8
    if declared > len(data) or declared < 44:
        raise ValueError("WAV truncado ou com tamanho RIFF inválido.")
    offset, has_fmt, has_audio = 12, False, False
    while offset + 8 <= declared:
        chunk_id = data[offset:offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > declared:
            raise ValueError("Chunk WAV truncado.")
        if chunk_id == b"fmt " and size >= 16:
            has_fmt = True
        if chunk_id == b"data" and size > 0:
            has_audio = True
        offset = end + (size % 2)
    if not has_fmt or not has_audio:
        raise ValueError("WAV sem descrição de formato ou sem amostras de áudio.")


def cached_audio(output, entry):
    if not isinstance(entry, dict):
        return False
    filename = entry.get("file")
    if not isinstance(filename, str) or "/" in filename or "\\" in filename or ":" in filename:
        return False
    try:
        data = (output / filename).read_bytes()
        validate_wav(data)
        return hashlib.sha256(data).hexdigest() == entry.get("sha256")
    except (OSError, ValueError):
        return False


def make_manifest(rows, payloads, cache, output, transform=None):
    manifest = {"activities": {}, "hints": {}, "success": [], "retry": []}
    for clip, text in rows:
        entry = cache.get(digest(payloads[clip], transform))
        if not cached_audio(output, entry):
            continue
        item = {"src": "assets/voice/" + entry["file"], "text": text}
        if "." not in clip:
            manifest[clip] = item
        else:
            group, key = clip.split(".", 1)
            if group in ("activities", "hints"):
                manifest[group][key] = item
            else:
                # Preserve a ordem do catálogo, omitindo falhas; não há placeholders inválidos.
                manifest[group].append(item)
    return manifest


def ensure_voice_exists(args):
    endpoint = "/get_predefined_voices" if args.voice else "/get_reference_files"
    data = get_json(args.server, endpoint, args.probe_timeout)
    names = set()
    if not isinstance(data, list):
        raise ValueError(f"Formato inesperado em {endpoint}; não foi possível validar a voz.")
    for item in data:
        if isinstance(item, str):
            names.add(item)
        elif isinstance(item, dict) and isinstance(item.get("filename"), str):
            names.add(item["filename"])
    selected = args.voice or args.reference
    if selected not in names:
        raise ValueError(f"O áudio {selected!r} não está listado em {endpoint}. Execute --probe e escolha um nome existente.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="URL do servidor já iniciado (padrão: loopback na porta 8000).")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--voice", type=basename, help="Filename exato de uma voz predefinida, escolhido pelo usuário.")
    selection.add_argument("--reference", type=basename, help="Filename exato de um áudio de referência existente, escolhido pelo usuário.")
    parser.add_argument("--probe", action="store_true", help="Lista vozes, referências e resposta de model-info; não gera áudio.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o plano sem chamar /tts e sem escrever arquivos.")
    parser.add_argument("--lines", type=Path, default=HERE / "lines.json")
    parser.add_argument("--output-dir", type=Path, default=HERE.parent / "dist" / "assets" / "voice")
    parser.add_argument("--only", action="append", default=[], help="Gera somente este identificador; pode repetir. Ex.: --only welcome.")
    parser.add_argument("--timeout", type=float, default=180, help="Timeout de geração por clipe em segundos.")
    parser.add_argument("--probe-timeout", type=float, default=3, help="Timeout separado por endpoint de consulta.")
    parser.add_argument("--pitch-semitones", type=float, default=-1.4, help="Ajuste de tom em semitons; 0 desativa o FFmpeg (padrão: -1.4).")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg", help="Executável FFmpeg com filtro rubberband (padrão: encontrado no PATH).")
    parser.add_argument("--force", action="store_true", help="Regenera os clipes selecionados, mesmo com cache válido.")
    args = parser.parse_args(argv)
    parsed = urlparse(args.server)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        parser.error("--server precisa ser uma URL HTTP/HTTPS sem credenciais, consulta ou fragmento.")
    if args.timeout <= 0 or args.probe_timeout <= 0:
        parser.error("Os timeouts devem ser positivos.")
    if not math.isfinite(args.pitch_semitones) or not -12 <= args.pitch_semitones <= 12:
        parser.error("--pitch-semitones deve ser finito e estar entre -12 e 12.")
    if args.probe:
        print(json.dumps(probe(args.server, args.probe_timeout), ensure_ascii=False, indent=2))
        return 0
    if not (args.voice or args.reference) and not args.dry_run:
        parser.error("Escolha explicitamente --voice ou --reference. Nenhuma voz é selecionada automaticamente.")
    try:
        rows = flatten_lines(read_json(args.lines))
        available = {clip for clip, _ in rows}
        unknown = set(args.only) - available
        if unknown:
            raise ValueError("Identificadores desconhecidos em --only: " + ", ".join(sorted(unknown)))
        chosen = [(clip, text) for clip, text in rows if not args.only or clip in args.only]
        payloads = {clip: payload_for(text, args.voice, args.reference) for clip, text in rows}
        transform = transform_for(args.pitch_semitones)
        if args.dry_run:
            print(json.dumps({"dry_run": True, "voice_selected": bool(args.voice or args.reference),
                              "notice": "Nenhuma chamada /tts; nenhuma escrita. Uma voz deve ser escolhida antes de gerar.",
                              "server": args.server, "output_dir": str(args.output_dir.resolve()),
                              "postprocess": transform,
                              "clips": [{"id": clip, "cache_key": digest(payloads[clip], transform), "payload": payloads[clip]} for clip, _ in chosen]},
                             ensure_ascii=False, indent=2))
            return 0
        ensure_voice_exists(args)
        ffmpeg = shutil.which(args.ffmpeg) or (str(Path(args.ffmpeg).resolve()) if Path(args.ffmpeg).is_file() else None)
        if args.pitch_semitones and not ffmpeg:
            raise ValueError("FFmpeg não encontrado. Use --ffmpeg CAMINHO ou --pitch-semitones 0 para desativar.")
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        index_path = output / "cache-index.json"
        index = read_json(index_path, {"version": 1, "entries": {}})
        if not isinstance(index, dict) or index.get("version") != 1 or not isinstance(index.get("entries"), dict):
            raise ValueError("cache-index.json inválido; preserve-o e use outro --output-dir para investigar.")
        entries = index["entries"]
        failures, succeeded, reused = {}, [], []
        for clip, text in chosen:
            payload = payloads[clip]
            key = digest(payload, transform)
            try:
                if not args.force and cached_audio(output, entries.get(key)):
                    reused.append(clip)
                    print(f"CACHE {clip}")
                else:
                    data = request(args.server, "/tts", args.timeout, payload)
                    validate_wav(data)
                    data = apply_pitch(data, transform, ffmpeg, args.timeout)
                    filename = clip.replace(".", "-") + "-" + key[:16] + ".wav"
                    atomic_bytes(output / filename, data)
                    entries[key] = {"file": filename, "sha256": hashlib.sha256(data).hexdigest(),
                                    "text": text, "payload": payload, "postprocess": transform, "created_at": utc_now()}
                    atomic_json(index_path, index)
                    succeeded.append(clip)
                    print(f"OK {clip}: {filename}")
            except (RuntimeError, ValueError, OSError) as exc:
                failures[clip] = {"error": str(exc), "cache_key": key, "failed_at": utc_now()}
                print(f"ERRO {clip}: {exc}", file=sys.stderr)
            # Atualiza após cada clipe: uma interrupção não perde os áudios já concluídos.
            atomic_json(output / "manifest.json", make_manifest(rows, payloads, entries, output, transform))
            atomic_json(output / "errors.json", {"updated_at": utc_now(), "clips": failures})
        print(json.dumps({"generated": succeeded, "cached": reused, "failed": list(failures),
                          "manifest": str(output / "manifest.json")}, ensure_ascii=False))
        return 2 if failures else 0
    except (RuntimeError, ValueError, OSError, TypeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
