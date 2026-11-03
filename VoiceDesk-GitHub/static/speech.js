/* Browser-provided speech recognition: no application API key required. */
(function (root) {
  function createVoiceInput({Recognition, onText, onState, onError, language, readText, setTimer=setTimeout, clearTimer=clearTimeout}) {
    let active=null, timer=null;
    function stop() { if(active) { onState('stopping'); active.stop(); } }
    function cancel() { if(active) active.abort(); }
    function start() {
      if(active) { stop(); return; }
      if(!Recognition) { onError('Speech input is not available in this browser. Open VoiceDesk in Chrome or Edge with speech recognition enabled, or type your complaint.'); return; }
      const recognition=new Recognition();
      active=recognition;
      const prefix=readText().trim();
      let finalText='', failed=false;
      recognition.lang=language();
      recognition.continuous=true;
      recognition.interimResults=true;
      recognition.onstart=()=>onState('listening');
      recognition.onresult=event=>{
        let interim='';
        for(let i=event.resultIndex;i<event.results.length;i++){
          if(event.results[i].isFinal) finalText+=event.results[i][0].transcript+' ';
          else interim+=event.results[i][0].transcript;
        }
        onText([prefix,finalText.trim(),interim.trim()].filter(Boolean).join(' ').slice(0,4000));
      };
      recognition.onerror=event=>{
        failed=true;
        const errors={
          'not-allowed':'Microphone access was denied. Allow microphone access for this site, then click Speak again.',
          'service-not-allowed':'This browser has disabled its speech service. Open VoiceDesk in Chrome or Edge, or type your complaint.',
          'audio-capture':'No microphone is available. Connect a microphone and check your device input settings.',
          'network':'The browser speech service could not connect. Check your internet connection, or open VoiceDesk in Chrome or Edge.',
          'no-speech':'No speech was detected. Click Speak and try again.',
          'language-not-supported':'This speech service does not support the selected language. Try English or another browser.'
        };
        if(event.error!=='aborted') onError(errors[event.error]||'Speech recognition stopped. Please try again.');
      };
      recognition.onend=()=>{
        clearTimer(timer);timer=null;active=null;
        onState('idle',!failed);
      };
      try { onState('starting'); recognition.start(); timer=setTimer(stop,120000); }
      catch(error){active=null;onState('idle',false);onError('Could not start speech recognition. Check microphone access and try again.');}
    }
    return {start,stop,cancel,isActive:()=>!!active};
  }
  root.createVoiceInput=createVoiceInput;
  if(typeof module!=='undefined') module.exports={createVoiceInput};
})(typeof window!=='undefined'?window:globalThis);
