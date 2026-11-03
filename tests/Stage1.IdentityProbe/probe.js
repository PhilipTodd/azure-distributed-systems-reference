(async()=>{
  const status=document.getElementById('status');
  const signin=document.getElementById('signin'),verify=document.getElementById('verify'),signout=document.getElementById('signout');
  function error(e){status.textContent='Verification needs attention: '+(e.errorCode||e.name||'Request failed');}
  async function bounded(promise,label,milliseconds=25000){
    let timer;
    try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject({errorCode:label+'_timeout — refresh this page before retrying'}),milliseconds);})]);}
    finally{clearTimeout(timer);}
  }
  verify.onclick=()=>{status.textContent='Preparing sign-in. Please wait for button 1 to become available.';};
  try{
  const config=await bounded(fetch('/config').then(r=>r.json()),'configuration');
  if(config.hosting) verify.textContent='2. Verify deployed hosting and OBO';
  const client=new msal.PublicClientApplication({auth:{clientId:config.clientId,authority:config.authority,knownAuthorities:['parameterpilotdev.ciamlogin.com'],redirectUri:'http://localhost:4200',postLogoutRedirectUri:'http://localhost:4200'},cache:{cacheLocation:'sessionStorage'},system:{loggerOptions:{piiLoggingEnabled:false,loggerCallback:()=>{}}}});
  await bounded(client.initialize(),'sign_in_initialisation');
  let response;
  response=await bounded(client.handleRedirectPromise(),'sign_in_return',45000);
  const account=response?.account||client.getAllAccounts()[0];
  if(account){client.setActiveAccount(account);status.textContent='Signed in as '+account.username+'. Click button 2 to run the checks.';signout.disabled=false;}else{status.textContent='Not signed in yet. Start with button 1, then return here to run the checks.';}
  signin.disabled=false;
  signin.onclick=()=>{status.textContent='Opening Microsoft customer sign-in…';client.loginRedirect({scopes:[config.trackingScope],prompt:'select_account'}).catch(error);};
  signout.onclick=()=>client.logoutRedirect({account:client.getActiveAccount()}).catch(error);
  verify.onclick=async()=>{
    if(!client.getActiveAccount()){
      status.textContent='Please click button 1 and complete email-passcode sign-in first. Then click button 2.';
      signin.focus();
      return;
    }
    verify.disabled=true;
    try{
      status.textContent='Step 1 of 3: obtaining the Tracking access token…';
      const tracking=await bounded(client.acquireTokenSilent({account:client.getActiveAccount(),scopes:[config.trackingScope],forceRefresh:true}),'tracking_token');
      status.textContent='Step 2 of 3: obtaining the Aquarium access token…';
      const aquarium=await bounded(client.acquireTokenSilent({account:client.getActiveAccount(),scopes:[config.aquariumScope],forceRefresh:true}),'aquarium_token');
      status.textContent=config.hosting?'Step 3 of 3: checking APIM, direct-access denials and deployed OBO (up to 3 minutes)…':'Step 3 of 3: validating tokens and running certificate-authenticated OBO (up to 60 seconds)…';
      const result=await fetch('/verify',{method:'POST',signal:AbortSignal.timeout(config.hosting?180000:60000),headers:{'Content-Type':'application/json','X-Probe-Key':config.requestKey},body:JSON.stringify({aquariumToken:aquarium.accessToken,trackingToken:tracking.accessToken})});
      if(!result.ok)throw{errorCode:result.status===403?'local_session_changed — refresh this page':'local_validation_http_'+result.status};
      const evidence=await result.json();
      const list=document.getElementById('results');list.replaceChildren();
      for(const check of evidence.checks){const row=document.createElement('li');row.className=check.passed?'pass':'fail';row.textContent=(check.passed?'PASS — ':'FAIL — ')+check.name+(check.error?' ('+check.error+')':'');list.appendChild(row);}
      status.textContent=evidence.passed?(config.hosting?'All deployed hosting checks passed.':'All identity checks passed. Sign out and verify account switching.'):'Some checks failed; review the safe result codes below.';
    }catch(e){error(e);if(e instanceof msal.InteractionRequiredAuthError){status.textContent+=' Use button 1 to sign in again.';}}
    finally{verify.disabled=false;}
  };
  }catch(e){error(e);}
})();
