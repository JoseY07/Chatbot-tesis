<?php
/**
 * Plugin Name: PGN Chatbot (Proxy Python)
 * Description: Shortcode [pgn_chatbot] que conecta con el backend FastAPI.
 * Version: 1.0.0
 */

if (!defined('ABSPATH')) exit;
if (!defined('PGN_CHATBOT_API_BASE')) {
  define('PGN_CHATBOT_API_BASE', 'https://TU-DOMINIO-PYTHON/api');
}

add_shortcode('pgn_chatbot', function() {
  wp_enqueue_script('pgn-chatbot-js', plugin_dir_url(__FILE__) . 'pgn-chatbot.js', array('jquery'), '1.0.0', true);
  wp_localize_script('pgn-chatbot-js', 'PGN_CHATBOT', array(
    'ajax_url' => admin_url('admin-ajax.php'),
    'nonce'    => wp_create_nonce('pgn_chatbot_nonce')
  ));
  ob_start(); ?>
  <div id="pgn-chatbot" style="max-width:600px">
    <div id="pgn-chat-log" style="border:1px solid #ddd;padding:10px;height:260px;overflow:auto;margin-bottom:8px"></div>
    <input id="pgn-chat-input" type="text" placeholder="Escribe tu consulta..." style="width:80%">
    <button id="pgn-chat-send">Enviar</button>
  </div>
  <?php return ob_get_clean();
});

add_action('wp_ajax_pgn_chat', 'pgn_chat_handler');
add_action('wp_ajax_nopriv_pgn_chat', 'pgn_chat_handler');
function pgn_chat_handler() {
  check_ajax_referer('pgn_chatbot_nonce');
  $mensaje = isset($_POST['mensaje']) ? sanitize_text_field($_POST['mensaje']) : '';
  if (!$mensaje) { wp_send_json_error(array('error' => 'Mensaje vacío'), 400); }
  $resp = wp_remote_post(PGN_CHATBOT_API_BASE . '/chat', array(
    'headers' => array('Content-Type' => 'application/json'),
    'body'    => wp_json_encode(array('mensaje' => $mensaje)),
    'timeout' => 15,
  ));
  if (is_wp_error($resp)) { wp_send_json_error(array('error' => $resp->get_error_message()), 500); }
  $code = wp_remote_retrieve_response_code($resp);
  $body = wp_remote_retrieve_body($resp);
  wp_send_json(array('status' => $code, 'data' => json_decode($body, true)), $code);
}
