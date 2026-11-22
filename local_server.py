"""Serve the game and optional loopback Chatterbox narration; no dependencies."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,json,urllib.request,urllib.error,hashlib,threading,os,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Parque dos Números com Chatterbox local')
parser.add_argument('--port',type=int,default=8765)
parser.add_argument('--reference',default='Briggs.mp3')
parser.add_argument('--chatterbox',default='http://127.0.0.1:8000')
parser.add_argument('--pitch-semitones',type=float,default=-1.4)
parser.add_argument('--exaggeration',type=float,default=.95)
args=parser.parse_args()
assert Path(args.reference).name==args.reference and '/' not in args.reference and '\\' not in args.reference
assert args.chatterbox.startswith(('http://127.0.0.1:','http://localhost:')),'O Chatterbox deve ser local.'
CACHE=ROOT/'.voice-cache';CACHE.mkdir(exist_ok=True)
lock=threading.Semaphore(1)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'dist'),**kw)
 def log_message(self,fmt,*a):
  # Keep player names and narration text out of the server log.
  if self.path.startswith('/api/'):return
  super().log_message(fmt,*a)
 def reply(self,status,data,mime='application/json'):
  if isinstance(data,dict):data=json.dumps(data,ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if self.path=='/api/voice/status':
   try:
    with urllib.request.urlopen(args.chatterbox+'/api/model-info',timeout=4) as r:info=json.load(r)
    self.reply(200,dict(available=bool(info.get('loaded') and info.get('supports_multilingual')),provider='Chatterbox',language='pt',local=True))
   except Exception:self.reply(200,dict(available=False,provider='Chatterbox',local=True))
  else:super().do_GET()
 def do_POST(self):
  if self.path!='/api/narrate':self.reply(404,dict(error='not_found'));return
  origin=self.headers.get('Origin')
  if origin and origin not in (f'http://127.0.0.1:{args.port}',f'http://localhost:{args.port}'):
   self.reply(403,dict(error='origin_not_allowed'));return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=8192:raise ValueError('Tamanho inválido')
   data=json.loads(self.rfile.read(size));text=data.get('text','')
   if not isinstance(text,str) or not 1<=len(text)<=800:raise ValueError('Texto inválido')
   payload=dict(text=text,voice_mode='clone',reference_audio_filename=args.reference,output_format='wav',language='pt',temperature=.7,exaggeration=args.exaggeration,cfg_weight=.5,seed=4096,speed_factor=1.,split_text=True,chunk_size=120,stream=False)
   key=hashlib.sha256(json.dumps(dict(payload=payload,pitch_semitones=args.pitch_semitones,projection='warm-authority-v1'),sort_keys=True).encode()).hexdigest();path=CACHE/(key+'.wav')
   with lock:
    if path.exists():audio=path.read_bytes()
    else:
     req=urllib.request.Request(args.chatterbox+'/tts',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
     with urllib.request.urlopen(req,timeout=180) as r:audio=r.read(24*1024*1024)
     if audio[:4]!=b'RIFF' or audio[8:12]!=b'WAVE':raise ValueError('Áudio inválido')
     if args.pitch_semitones:
      with tempfile.NamedTemporaryFile(dir=CACHE,suffix='.wav',delete=False) as f:tempname=f.name
      try:
       shift=2**(args.pitch_semitones/12)
       filt=f'rubberband=pitch={shift}:tempo=1:formant=preserved:pitchq=quality,equalizer=f=180:t=q:w=1:g=1.5,acompressor=threshold=0.12:ratio=2.2:attack=8:release=100:makeup=1.3,alimiter=limit=0.94:level=disabled'
       subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i','pipe:0','-af',filt,'-c:a','pcm_s16le',tempname],input=audio,check=True,capture_output=True,timeout=45)
       audio=Path(tempname).read_bytes()
      finally:Path(tempname).unlink(missing_ok=True)
     temp=path.with_suffix('.tmp');temp.write_bytes(audio);os.replace(temp,path)
   self.reply(200,audio,'audio/wav')
  except (BrokenPipeError,ConnectionResetError):pass
  except Exception:self.reply(503,dict(error='voice_unavailable'))
server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
print(f'Parque: http://127.0.0.1:{args.port}',flush=True)
print('Narracao: Chatterbox local, referencia '+args.reference+'; portugues; cache privado fora de dist.',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
