#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>

const char* ssid = "LumiKONline";
const char* password = "";

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.printf("Cliente conectado: %u\n", client->id());
  } 
  else if (type == WS_EVT_DISCONNECT) {
    Serial.printf("Cliente desconectado: %u\n", client->id());
  } 
  else if (type == WS_EVT_DATA) {
    AwsFrameInfo *info = (AwsFrameInfo*)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      data[len] = 0;
      String msg = (char*)data;
      ws.textAll(msg);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  if (!SPIFFS.begin(true)) {
    Serial.println("Error al montar SPIFFS");
    return;
    File root = SPIFFS.open("/");
    File file = root.openNextFile();

    while(file){
        Serial.print("FILE: ");
        Serial.println(file.name());
        file = root.openNextFile();
    }
  }

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP: ");
  Serial.println(IP);

  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/control.html", "text/html");
});

server.on("/assistant", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/assistant.html", "text/html");
});

server.on("/favicon.ico", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/favicon.ico", "image/x-icon");
});

  server.begin();
  Serial.println("Servidor iniciado");
}

void loop() {
  ws.cleanupClients();
  delay(10);
}
