# ==============================================================
# ACTIVIDAD: SERIE TEMPORAL DE UNA VARIABLE DE INGENIERÍA CIVIL
# Variable: Desplazamiento horizontal (mm)
# Proyecto: Edificio Multifamiliar Los Álamos
# Herramienta: Plotly
# ==============================================================

# 1. IMPORTAR LIBRERÍAS
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.colab import files

# 2. CARGAR EL EXCEL DE DATOS
# Ejecuta esta celda y selecciona:
# Datos_Monitoreo_Estructural_Serie_Temporal.xlsx
uploaded = files.upload()
archivo = next(iter(uploaded))

datos = pd.read_excel(archivo, sheet_name="Datos_Monitoreo")
datos["Fecha"] = pd.to_datetime(datos["Fecha"])

print("Primeros registros:")
display(datos.head())

# 3. PARÁMETROS DE LA ACTIVIDAD
variable = "Desplazamiento horizontal"
unidad = "mm"

# Criterio ilustrativo para identificar cambios importantes.
# Este valor se usa con fines académicos, no como límite normativo.
umbral_cambio = 0.35

# 4. PREPARACIÓN DE LA SERIE TEMPORAL
datos = datos.sort_values("Fecha").copy()
datos["Cambio_calculado"] = datos["Valor"].diff()
datos["Promedio_movil_3d"] = datos["Valor"].rolling(window=3, min_periods=1).mean()
datos["Cambio_importante"] = datos["Cambio_calculado"].abs() >= umbral_cambio

print("\nResumen estadístico:")
display(datos[["Valor", "Cambio_calculado", "Promedio_movil_3d"]].describe())

# 5. GRÁFICO INTERACTIVO PRINCIPAL
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=datos["Fecha"],
    y=datos["Valor"],
    mode="lines+markers",
    name="Desplazamiento",
    hovertemplate="Fecha: %{x|%d/%m/%Y}<br>Desplazamiento: %{y:.2f} mm<extra></extra>"
))

fig.add_trace(go.Scatter(
    x=datos["Fecha"],
    y=datos["Promedio_movil_3d"],
    mode="lines",
    name="Promedio móvil 3 días",
    line=dict(dash="dash"),
    hovertemplate="Fecha: %{x|%d/%m/%Y}<br>Promedio móvil: %{y:.2f} mm<extra></extra>"
))

cambios = datos[datos["Cambio_importante"]].copy()

fig.add_trace(go.Scatter(
    x=cambios["Fecha"],
    y=cambios["Valor"],
    mode="markers",
    name="Cambio importante",
    marker=dict(size=12, symbol="diamond"),
    customdata=cambios[["Cambio_calculado"]],
    hovertemplate=(
        "CAMBIO IMPORTANTE<br>"
        "Fecha: %{x|%d/%m/%Y}<br>"
        "Valor: %{y:.2f} mm<br>"
        "Δ diario: %{customdata[0]:+.2f} mm"
        "<extra></extra>"
    )
))

fig.update_layout(
    title="Monitoreo temporal del desplazamiento horizontal – Edificio Multifamiliar Los Álamos",
    xaxis_title="Fecha (eje temporal)",
    yaxis_title="Desplazamiento horizontal (mm)",
    template="plotly_white",
    hovermode="x unified",
    legend_title="Serie"
)

# Control interactivo de rango temporal
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=7, label="7 días", step="day", stepmode="backward"),
            dict(count=14, label="14 días", step="day", stepmode="backward"),
            dict(step="all", label="Todo")
        ])
    )
)

fig.show()

# 6. TABLA DE CAMBIOS IMPORTANTES
tabla_cambios = cambios[
    ["Fecha", "Valor", "Cambio_calculado", "Clasificación", "Observación"]
].copy()

tabla_cambios["Fecha"] = tabla_cambios["Fecha"].dt.strftime("%d/%m/%Y")
tabla_cambios = tabla_cambios.rename(columns={
    "Valor": "Desplazamiento (mm)",
    "Cambio_calculado": "Cambio diario (mm)"
})

print("\nCambios importantes identificados:")
display(tabla_cambios)

# 7. INTERPRETACIÓN AUTOMÁTICA BÁSICA
inicial = datos["Valor"].iloc[0]
final = datos["Valor"].iloc[-1]
maximo = datos["Valor"].max()
fecha_max = datos.loc[datos["Valor"].idxmax(), "Fecha"]
variacion_pct = (final - inicial) / inicial * 100
n_cambios = int(datos["Cambio_importante"].sum())

print("\nINTERPRETACIÓN:")
print(
    f"La serie presenta una tendencia general creciente: pasa de {inicial:.2f} mm "
    f"a {final:.2f} mm, equivalente a una variación acumulada de {variacion_pct:.1f}%. "
    f"El valor máximo fue {maximo:.2f} mm el {fecha_max.strftime('%d/%m/%Y')}. "
    f"Con el criterio ilustrativo |Δ diario| ≥ {umbral_cambio:.2f} mm se identificaron "
    f"{n_cambios} cambios importantes. Estos eventos deben revisarse junto con las "
    f"condiciones reales de medición y el estado del sensor; no deben interpretarse "
    f"automáticamente como una falla estructural."
)

# 8. GRÁFICO COMPLEMENTARIO DE CAMBIO DIARIO
fig2 = px.bar(
    datos,
    x="Fecha",
    y="Cambio_calculado",
    title="Variación diaria del desplazamiento horizontal",
    labels={
        "Fecha": "Fecha",
        "Cambio_calculado": "Cambio diario (mm)"
    }
)
fig2.add_hline(y=umbral_cambio, line_dash="dash",
               annotation_text=f"+{umbral_cambio:.2f} mm")
fig2.add_hline(y=-umbral_cambio, line_dash="dash",
               annotation_text=f"-{umbral_cambio:.2f} mm")
fig2.update_layout(template="plotly_white")
fig2.show()
