from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pywifi
import time
import speedtest


# Creazione dell'app Dash
app = Dash(__name__)
app.title = "WiFi Performance Analyzer"

# Layout dell'app
app.layout = html.Div(
    style={
        'fontFamily': 'Arial, sans-serif',
        'padding': '20px',
        'backgroundColor': '#1e1e2f',
        'maxWidth': '800px',
        'margin': 'auto',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.3)',
        'borderRadius': '12px'
    },
    children=[
        html.H1("WiFi Performance Analyzer", style={
            'textAlign': 'center',
            'color': '#ffffff'
        }),
        
        dcc.Loading(
            id="loading-scan-networks",
            type="circle",
            children=[
                html.Div(id="network-scan-results", style={
                    'marginBottom': '20px',
                    'padding': '10px',
                    'backgroundColor': '#29293d',
                    'border': '1px solid #444',
                    'borderRadius': '8px',
                    'color': '#ffffff'
                }, children=[
                    html.P("Click 'Scan Networks' to see available Wi-Fi networks.", style={'textAlign': 'center'})
                ])
            ]
        ),
        
        html.Div(style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
            html.Button(
                "Scan Networks", 
                id="scan-networks-button", 
                style={
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'color': '#ffffff',
                    'backgroundColor': '#0078d4',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                }
            )
        ]),
        
        html.Div(style={'textAlign': 'center'}, children=[
            html.Button(
                "Run Speed Test", 
                id="run-speedtest-button", 
                style={
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'color': '#ffffff',
                    'backgroundColor': '#28a745',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'marginBottom': '20px'
                }
            ),
            dcc.Loading(
                id="loading-speedtest",
                type="circle",
                children=[
                    html.Div(id="speedtest-results", style={
                        'marginTop': '20px',
                        'padding': '10px',
                        'backgroundColor': '#29293d',
                        'border': '1px solid #444',
                        'borderRadius': '8px',
                        'color': '#ffffff'
                    }),
                    dcc.Graph(id="speed-gauge", style={
                        'marginTop': '20px'
                    })
                ]
            )
        ])
    ]
)

# Funzione per effettuare la scansione delle reti Wi-Fi
def scan_networks():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(3)  # Simulazione del tempo necessario per la scansione
    networks = iface.scan_results()

    # Filtrare duplicati basati sull'SSID
    unique_networks = {}
    for network in networks:
        if network.ssid not in unique_networks or network.signal > unique_networks[network.ssid]:
            unique_networks[network.ssid] = network.signal  # Conserva il segnale più forte

    return [{"SSID": ssid, "Signal": signal} for ssid, signal in unique_networks.items()]


# Callback per la scansione delle reti
@app.callback(
    Output("network-scan-results", "children"),
    Input("scan-networks-button", "n_clicks")
)
def display_networks(n_clicks):
    if not n_clicks:
        return html.P("Click 'Scan Networks' to see available Wi-Fi networks.")
    networks = scan_networks()  # Chiama la funzione aggiornata
    if not networks:
        return html.P("No networks found. Please try again.", style={'textAlign': 'center', 'color': 'red'})
    
    # Creazione del grafico per la potenza del segnale
    ssids = [net['SSID'] for net in networks]
    signals = [net['Signal'] for net in networks]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ssids, 
        y=signals, 
        text=[f"{signal} dBm" for signal in signals],
        textposition='auto',
        marker_color='#4caf50',
    ))
    fig.update_layout(
        title="Wi-Fi Signal Strength",
        xaxis_title="SSID",
        yaxis_title="Signal Strength (dBm)",
        yaxis=dict(autorange='reversed'),  # Invertire l'asse Y
        template="plotly_dark",
    )

    return html.Div([
        html.H3("Available Networks:", style={'color': '#ffffff'}),
        dcc.Graph(figure=fig)
    ])

def display_networks(n_clicks):
    if not n_clicks:
        return html.P("Click 'Scan Networks' to see available Wi-Fi networks.")
    networks = scan_networks()
    if not networks:
        return html.P("No networks found. Please try again.", style={'textAlign': 'center', 'color': 'red'})
    
    # Creazione del grafico per la potenza del segnale
    ssids = [net['SSID'] for net in networks]
    signals = [net['Signal'] for net in networks]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ssids, 
        y=signals, 
        text=[f"{signal} dBm" for signal in signals],
        textposition='auto',
        marker_color='#4caf50',
    ))
    fig.update_layout(
        title="Wi-Fi Signal Strength",
        xaxis_title="SSID",
        yaxis_title="Signal Strength (dBm)",
        yaxis=dict(autorange='reversed'),  # Invertire l'asse Y
        template="plotly_dark",
    )

    return html.Div([
        html.H3("Available Networks:", style={'color': '#ffffff'}),
        dcc.Graph(figure=fig)
    ])

# Funzione per il test di velocità
def run_speed_test():
    st = speedtest.Speedtest()
    st.get_best_server()
    ping = st.results.ping
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000      # Convert to Mbps
    return ping, download_speed, upload_speed

# Callback per il test di velocità
@app.callback(
    [Output("speedtest-results", "children"), Output("speed-gauge", "figure")],
    Input("run-speedtest-button", "n_clicks")
)
def display_speed_test(n_clicks):
    if not n_clicks:
        return html.P("Click 'Run Speed Test' to see results."), go.Figure()
    
    time.sleep(2)  # Simulazione del caricamento
    ping, download_speed, upload_speed = run_speed_test()
    results_text = html.Div([
        html.P(f"Ping: {ping:.2f} ms", style={'color': '#ffffff'}),
        html.P(f"Download Speed: {download_speed:.2f} Mbps", style={'color': '#ffffff'}),
        html.P(f"Upload Speed: {upload_speed:.2f} Mbps", style={'color': '#ffffff'})
    ])

    # Grafico gauge per la velocità di download
    gauge_figure = go.Figure(go.Indicator(
        mode="gauge+number",
        value=download_speed,
        title={'text': "Download Speed (Mbps)"},
        gauge={
            'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "#ffffff"},
            'bar': {'color': "#00ff00"},
            'steps': [
                {'range': [0, 50], 'color': "#f44336"},
                {'range': [50, 100], 'color': "#ffeb3b"},
                {'range': [100, 150], 'color': "#228b22"},
                {'range': [150, 200], 'color': "#2196f3"}
            ],
        }
    ))
    gauge_figure.update_layout(
        paper_bgcolor="#1e1e2f",
        font={'color': "#ffffff", 'family': "Arial"}
    )

    return results_text, gauge_figure

# Avvio del server Dash
if __name__ == "__main__":
    app.run_server(debug=True)
