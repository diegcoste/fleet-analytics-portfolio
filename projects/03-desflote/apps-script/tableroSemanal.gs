/**
 * tableroSemanal()
 * Construye la tabla semanal de forecast vs ventas reales del desflote.
 *
 * - Lee ventas de HISTORIAL_VENTAS y forecast de PROYECCION.
 * - Deduplica por VIN (una venta cuenta una sola vez: la de pago más reciente).
 * - Asigna cada semana (lunes–domingo) al mes de su JUEVES.
 * - Escribe el resultado en TABLERO_SEMANAL sin tocar las hojas fuente.
 */

const CFG = {
  hojaVentas: 'HISTORIAL_VENTAS',
  hojaForecast: 'PROYECCION',
  hojaSalida: 'TABLERO_SEMANAL',
  colVin: 0,
  colFechaPago: 7,
  colMonto: 8,
  tz: 'America/Mexico_City',
};

function tableroSemanal() {
  const ss = SpreadsheetApp.getActive();
  const ventas = leerVentasDeduplicadas_(ss.getSheetByName(CFG.hojaVentas));
  const forecast = leerForecast_(ss.getSheetByName(CFG.hojaForecast));

  // Agregar ventas por semana
  const porSemana = new Map();
  ventas.forEach(v => {
    const lunes = lunesDe_(v.fecha);
    const key = fmt_(lunes);
    const acc = porSemana.get(key) || { lunes, unidades: 0, monto: 0 };
    acc.unidades += 1;
    acc.monto += v.monto;
    porSemana.set(key, acc);
  });

  // Unir con forecast y armar salida ordenada
  const llaves = new Set([...porSemana.keys(), ...forecast.keys()]);
  const filas = [...llaves].sort().map(k => {
    const r = porSemana.get(k) || { lunes: parse_(k), unidades: 0, monto: 0 };
    const f = forecast.get(k) || 0;
    const cumplimiento = f > 0 ? r.unidades / f : '';
    return [k, mesPorJueves_(r.lunes), f, r.unidades, cumplimiento, r.monto];
  });

  const out = ss.getSheetByName(CFG.hojaSalida) || ss.insertSheet(CFG.hojaSalida);
  out.clearContents();
  out.getRange(1, 1, 1, 6).setValues([[
    'semana_lunes', 'mes', 'forecast_unidades', 'ventas_unidades', '% cumplimiento', 'monto_cobrado',
  ]]);
  if (filas.length) out.getRange(2, 1, filas.length, 6).setValues(filas);
  out.getRange(2, 5, Math.max(filas.length, 1), 1).setNumberFormat('0.0%');
}

/** Una venta por VIN: se queda la de fecha de pago más reciente. */
function leerVentasDeduplicadas_(sh) {
  const data = sh.getDataRange().getValues().slice(1);
  const porVin = new Map();
  data.forEach(r => {
    const vin = String(r[CFG.colVin]).trim().toUpperCase();
    const fecha = r[CFG.colFechaPago];
    if (!vin || !(fecha instanceof Date)) return;
    const prev = porVin.get(vin);
    if (!prev || fecha > prev.fecha) {
      porVin.set(vin, { vin, fecha, monto: Number(r[CFG.colMonto]) || 0 });
    }
  });
  return [...porVin.values()];
}

/** Forecast por semana: columna A = lunes de la semana, B = unidades. */
function leerForecast_(sh) {
  const m = new Map();
  sh.getDataRange().getValues().slice(1).forEach(r => {
    if (r[0] instanceof Date) m.set(fmt_(lunesDe_(r[0])), Number(r[1]) || 0);
  });
  return m;
}

function lunesDe_(d) {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const dow = (x.getDay() + 6) % 7; // lunes = 0
  x.setDate(x.getDate() - dow);
  return x;
}

/** La semana pertenece al mes en que cae su jueves. */
function mesPorJueves_(lunes) {
  const jueves = new Date(lunes);
  jueves.setDate(lunes.getDate() + 3);
  return Utilities.formatDate(jueves, CFG.tz, 'yyyy-MM');
}

function fmt_(d) { return Utilities.formatDate(d, CFG.tz, 'yyyy-MM-dd'); }
function parse_(s) { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); }
