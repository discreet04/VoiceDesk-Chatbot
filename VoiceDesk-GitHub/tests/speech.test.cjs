const {test}=require('node:test');
const assert=require('node:assert/strict');
const {createVoiceInput}=require('../static/speech.js');
function setup(Recognition){
 let value='Existing details',state='',error='',instance;
 class FakeRecognition{
  constructor(){instance=this}
  start(){this.onstart()}
  stop(){this.onend()}
  abort(){this.onerror({error:'aborted'});this.onend()}
 }
 const control=createVoiceInput({Recognition:Recognition===null?null:FakeRecognition,readText:()=>value,language:()=>'hi-IN',onText:v=>value=v,onState:s=>state=s,onError:e=>error=e,setTimer:()=>1,clearTimer:()=>{}});
 return {control,get value(){return value},get state(){return state},get error(){return error},get instance(){return instance}};
}
test('speech becomes editable complaint text without an API call',()=>{
 const s=setup();s.control.start();assert.equal(s.instance.lang,'hi-IN');assert.equal(s.state,'listening');
 const result=[{transcript:'wifi nahi chal raha'}];result.isFinal=false;
 s.instance.onresult({resultIndex:0,results:[result]});assert.equal(s.value,'Existing details wifi nahi chal raha');
 result.isFinal=true;s.instance.onresult({resultIndex:0,results:[result]});
 const next=[{transcript:'room 204'}];next.isFinal=true;
 s.instance.onresult({resultIndex:1,results:[result,next]});
 assert.equal(s.value,'Existing details wifi nahi chal raha room 204');
 s.control.stop();assert.equal(s.state,'idle');assert.equal(s.control.isActive(),false);
});
test('unsupported browser gets actionable error',()=>{const s=setup(null);s.control.start();assert.match(s.error,/not available/);assert.equal(s.control.isActive(),false)});
test('permission failure and end release recording state',()=>{const s=setup();s.control.start();s.instance.onerror({error:'not-allowed'});s.instance.onend();assert.match(s.error,/Microphone access was denied/);assert.equal(s.state,'idle')});
test('second click stops and cancellation preserves text',()=>{const s=setup();s.control.start();s.control.start();assert.equal(s.state,'idle');s.control.start();s.control.cancel();assert.equal(s.value,'Existing details');assert.equal(s.control.isActive(),false)});
