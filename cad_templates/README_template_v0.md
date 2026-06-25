# Ache Innovation — Template CAD v0

Este template es el primer punto de partida CAD para una prótesis canina externa funcional.

## Archivo principal
`ache_canine_prosthesis_template_v0.scad`

Se abre con OpenSCAD.

## Qué representa
- socket superior para muñón;
- bandas/correas;
- caña estructural curva;
- refuerzos laterales;
- pie protésico tipo pad/rocker;
- suela inferior;
- flecha de orientación frontal.

## Qué NO representa todavía
- validación clínica;
- anatomía perfecta;
- diseño final fabricable sin revisión;
- ajuste real de liner interno;
- simulación biomecánica.

## Cómo usar
1. Abrir `.scad` en OpenSCAD.
2. Ajustar parámetros superiores.
3. Renderizar con F6.
4. Exportar STL.
5. Revisar con veterinario/diseñador/impresor.

## Próximo desarrollo de software
Conectar estos parámetros desde la app:
- prosthesis_length;
- socket_depth;
- socket_top_diam_x/y;
- socket_bottom_diam_x/y;
- pylon_diam;
- foot_length;
- foot_width;
- limb_type;
- side.
