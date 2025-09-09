(function(){
  function addMsg(who, text){
    const el = document.getElementById('pgn-chat-log');
    const row = document.createElement('div');
    row.textContent = who + ': ' + text;
    el.appendChild(row);
    el.scrollTop = el.scrollHeight;
  }
  document.addEventListener('DOMContentLoaded', function(){
    const input = document.getElementById('pgn-chat-input');
    const btn   = document.getElementById('pgn-chat-send');
    btn.addEventListener('click', function(){
      const mensaje = input.value.trim();
      if(!mensaje) return;
      addMsg('Tú', mensaje);
      input.value = '';
      const form = new FormData();
      form.append('action', 'pgn_chat');
      form.append('mensaje', mensaje);
      form.append('_ajax_nonce', PGN_CHATBOT.nonce);
      fetch(PGN_CHATBOT.ajax_url, { method: 'POST', body: form })
        .then(r => r.json()).then(json => {
          if(json && json.data){ addMsg('PGN', json.data.respuesta || '(sin respuesta)'); }
          else { addMsg('PGN', 'Error de comunicación'); }
        }).catch(() => addMsg('PGN', 'Error de red'));
    });
  });
})();