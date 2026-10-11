import json, math, pickle, os, shutil, networkx as nx
SP='/tmp/claude-0/-home-user-App-visitas/337edbc6-130b-5668-97df-f033ed5dc189/scratchpad/'
OUT='/home/user/App-visitas/'
W='Wikimedia Commons'
def img(f,cap,credit=W,year=None): return {'src':'img/'+f+'.webp','cap':cap,'credit':credit,**({'year':year} if year else {})}
BUS_OUT=[dict(t='12:40',best=True),dict(t='12:45'),dict(t='13:50',label='el siguiente: 1 h más')]
BUS_BACK=[dict(t='18:50'),dict(t='19:10',label='sobrados'),dict(t='19:40',best=True,label='el vuestro'),dict(t='20:00',bad=True,label='llega 20:14: no')]
BUS_NOTE_OUT='Horario de domingo según Moovit. Parada en la explanada de salida de la estación, rótulo «11 Acueducto». 2,25 € (billete AVE), en efectivo o con tarjeta o móvil sin contacto. Si veis antes el 12, también os deja en el centro.'
BUS_NOTE_BACK='Horario de domingo según Moovit. Parada Acueducto 3, en la plaza de Artillería, a 2 min del Azoguejo. Rótulo «11 Estación AVE». Unos 15 min hasta Guiomar. El de las 19:40 llega hacia las 19:54: 24 min de margen para vuestro Avant de las 20:18. Va lleno: estad en la parada a las 19:25.'
stops=[
 dict(id='guiomar',n='0',short='Estación',name='Llegada: estación Segovia-Guiomar',kind='train',zone='Llegada',time='12:32',alert='Avant 08129 · llega 12:32',stay=10,lat=40.91010,lon=-4.09490,gq='Estación de Segovia-Guiomar',
  hook='Salid rápido del andén: el autobús 11 espera en la puerta y en el puente se llena.',audio='audio/00.mp3',dur=53,
  images=[img('guiomar-b','Las vías de Segovia-Guiomar con la sierra de Guadarrama al fondo'),img('guiomar-a','El edificio de la estación')],
  deps=dict(title='Bus 11 · Guiomar → Acueducto',note=BUS_NOTE_OUT,list=BUS_OUT),
  look='Las dársenas de autobús están justo delante del edificio de la estación. Buscad el 11, con destino Acueducto.',
  info=[dict(t='Si se os escapa',p='El siguiente 11 no sale hasta las 13:50. Alternativas: la línea 12 (también va al centro, a la avenida del Acueducto) o taxi desde la parada de la estación: unos 11-12 € en domingo y 10-12 min.'),
        dict(t='Horario en directo',p='App «Urbanos de Segovia» (Avanza) o Moovit. Atención al cliente de Avanza:',tel='900 925 303'),
        dict(t='Reservad la comida ahora',badge='IMPORTANTE',bc='hot',p='La Cueva de San Esteban solo tiene 32 plazas y es puente. Pedid mesa para las 14:30.',tel='921 460 982')],
  facts=[dict(tag='SALSEO',title='Una estación con nombre de amante',text='Guiomar era el nombre en clave con el que Machado escribía a Pilar de Valderrama, su amor secreto y casada. La estación se inauguró en 2007 con ese nombre.'),
         dict(tag='CIFRA',title='Bajo la sierra',text='Para llegar aquí el tren cruza el Guadarrama por un túnel de unos 28 km, el túnel ferroviario más largo de España.'),
         dict(tag='TIP',title='Primero, la foto del acueducto',text='El bus os deja a 2 minutos del Azoguejo. Dadle al play de la parada 1 cuando lo veáis aparecer.')]),
 dict(id='acueducto',n='1',short='Acueducto',name='Acueducto y Azoguejo',zone='Zona baja',time='13:00',stay=15,lat=40.94787,lon=-4.11815,gq='Plaza del Azoguejo, Segovia',
  hook='Casi 2.000 años en pie, 20.000 bloques de granito y ni una gota de cemento.',audio='audio/01.mp3',dur=59,
  images=[img('acueducto-arcos','Los arcos desde abajo: puro equilibrio'),img('azoguejo','La vista desde la calle Real hacia el Azoguejo'),img('acueducto-noche','De noche se ilumina y el granito se vuelve dorado'),img('acueducto-antiguo','El acueducto en una fotografía del siglo XIX',year='s. XIX')],
  look='Los agujeritos en los bloques: ahí se enganchaban las tenazas para subirlos. Y arriba, las hornacinas con figuras.',
  facts=[dict(tag='DATO',title='La loba que vino de Roma',text='La loba con Rómulo y Remo junto a los arcos fue un regalo de Roma en 1974 por el «bimilenario» del acueducto. Detalle friki: si se construyó a finales del siglo I d.C., aún no cumplía 2.000 años. La fiesta se hizo igual.'),dict(tag='DATO',title='36 arcos y un fraile',text='En 1072 un ataque de las tropas de Al-Mamún de Toledo tumbó 36 arcos. Con los Reyes Católicos, fray Juan de Escobedo, monje de El Parral, los rehízo con mimo para imitar el original romano.'),
         dict(tag='CIFRA',title='Sin cemento',text='Unos 20.400 bloques de granito sin argamasa. Se sostienen solo por el peso y la geometría de los arcos.'),
         dict(tag='LEYENDA',title='El diablo y la aguadora',text='Una aguadora vendió su alma al diablo para que le subiera el agua en una noche. Cantó el gallo cuando faltaba una piedra y se libró.',legend='Leyenda popular'),
         dict(tag='DATO',title='Coches bajo los arcos',text='Durante décadas el tráfico pasó por debajo, autobuses incluidos. Se cortó en 1992, cuando arrancó una gran restauración del arquitecto Francisco Jurado que duró casi ocho años.'),
         dict(tag='FECHA',title='Patrimonio de la Humanidad',text='En 1985 la UNESCO declaró Patrimonio Mundial la ciudad vieja de Segovia junto a su acueducto.'),
         dict(tag='FAMOSOS',title='El mesón de las fotos',text='A los pies del acueducto está el Mesón de Cándido, donde el cochinillo se corta con un plato. Por sus mesas pasaron Orson Welles, Adolfo Suárez o Kofi Annan. ¿Hemingway? Se repite mucho, pero sin pruebas.')],
  numbers=[dict(v='28,10',u='m',l='altura máxima, aquí en el Azoguejo'),dict(v='167',l='arcos'),dict(v='~20.400',l='bloques de granito'),dict(v='15',u='km',l='desde la sierra (río Frío)')],
  chart=dict(title='¿Cómo de alto es?',max=30,rows=[dict(l='Acueducto',v=28,t='28,1 m',hl=True),dict(l='Edificio 9 plantas',v=27,t='27 m'),dict(l='Árbol grande',v=15,t='15 m'),dict(l='Autobús',v=3.2,t='3 m')],note='Comparativa aproximada.'),
  ba=dict(before='img/acueducto-1838.webp',after='img/azoguejo.webp',by='1838',ay='Hoy',cap='En 1838 el Azoguejo era un mercado con casas pegadas a los pilares. Hoy la plaza está despejada y peatonal.'),
  timeline=[dict(y='s. I-II',e='Roma levanta el acueducto'),dict(y='1072',e='Las tropas de Al-Mamún de Toledo destruyen 36 arcos'),dict(y='desde 1484',e='Fray Juan de Escobedo los rehace para los Reyes Católicos'),dict(y='1985',e='Patrimonio de la Humanidad'),dict(y='1992',e='Se corta el tráfico y empieza la gran restauración')]),
 dict(id='mirador',n='2',short='Mirador',name='Mirador del Postigo del Consuelo',zone='Zona baja',time='13:18',stay=5,lat=40.94856,lon=-4.11833,gq='Postigo del Consuelo, Segovia',
  hook='Subid las escaleras pegadas al acueducto: aquí está la foto de pareja.',audio='audio/02.mp3',dur=58,
  images=[img('acueducto-08','El acueducto entero desde lo alto, con el Azoguejo abajo'),img('acueducto-arcos','Las dos filas de arcos')],
  look='El canal por donde corría el agua, en lo alto del acueducto, casi a la altura de vuestros ojos.',
  facts=[dict(tag='SALSEO',title='El diablo del selfi',text='En 2019 Segovia puso en la calle San Juan un diablillo de 1,70 m, obra de José Antonio Abella, haciéndose un selfi con el acueducto. Una asociación católica lo vio ofensivo, juntó miles de firmas y fue a los tribunales. Ahí sigue, posando.'),dict(tag='FAMOSOS',title='Posando desde 1853',text='Hacia 1853 el galés Charles Clifford, fotógrafo al servicio de Isabel II, retrató el acueducto. Sus copias acabaron en la Royal Collection británica: ya posaba para la realeza en tiempos de la reina Victoria.'),
         dict(tag='DATO',title='Un sudoku romano',text='La inscripción de bronce desapareció, pero en 1992 Géza Alföldy reconstruyó el texto a partir de los agujeros de los clavos. Eso sí, no todos los expertos compran su lectura.'),
         dict(tag='CIFRA',title='Pendiente mínima',text='El agua bajaba por gravedad con una pendiente casi imperceptible a lo largo de unos 15 km.'),
         dict(tag='TIP',title='Foto',text='Poneos de espaldas a la barandilla con el acueducto en diagonal: sale entero con la ciudad nueva al fondo.')],
  numbers=[dict(v='2',l='filas de arcos en la parte alta'),dict(v='4,50',u='m',l='luz media de cada arco')]),
 dict(id='picos',n='3',short='Casa de los Picos',name='Casa de los Picos',zone='Calle Real',time='13:25',stay=4,lat=40.94803,lon=-4.12058,gq='Casa de los Picos, Segovia',
  hook='Más de 600 puntas de diamante en una fachada. ¿Ostentación o algo más?',audio='audio/03.mp3',dur=52,
  images=[img('picos','La fachada de los picos en la calle Juan Bravo')],
  look='Mirad la fachada en diagonal desde la esquina: los picos hacen un efecto óptico con la luz.',
  facts=[dict(tag='DATO',title='Culebrón inmobiliario',text='Ni la autoría está clara: unos dicen que la levantó Juan de la Hoz y otros que fue Pedro López de Ayala y los De la Hoz la compraron después. Lo seguro: hacia 1500 el regidor Juan de la Hoz la hizo su casa y le puso fachada nueva.'),dict(tag='DATO',title='Moda italiana',text='El almohadillado en punta de diamante era una moda de inspiración italiana, pero forrar la fachada entera era rarísimo. Por eso es una de las casas más fotografiadas de Segovia.'),
         dict(tag='CIFRA',title='617 picos',text='Es la cifra que se suele dar: más de seiscientos bloques tallados en punta de diamante.'),
         dict(tag='MITO',title='¿Por qué los picos?',text='Hay varias versiones: ostentación de una familia noble, defensa junto a la muralla o una forma de acallar habladurías. Ninguna está probada.',legend='Origen discutido'),
         dict(tag='DATO',title='Hoy, Escuela de Arte',text='Los alumnos de la Escuela de Arte y Superior de Diseño entran cada mañana bajo las seiscientas puntas.')],
  numbers=[dict(v='617',l='picos de granito'),dict(v='h. 1500',l='Juan de la Hoz le pone fachada nueva')]),
 dict(id='sanmartin',n='4',short='Juan Bravo',name='Plaza de San Martín y Juan Bravo',zone='Calle Real',time='13:31',stay=5,lat=40.94870,lon=-4.12157,gq='Plaza de Medina del Campo, Segovia',
  hook='El rebelde que plantó cara a Carlos I y perdió la cabeza por ello.',audio='audio/04.mp3',dur=60,
  images=[img('juanbravo','Juan Bravo de noche, con la Casa del Siglo XV detrás'),img('sanmartin','San Martín y su galería porticada románica')],
  look='La estatua de Juan Bravo con el estandarte, y detrás la galería porticada de San Martín.',
  facts=[dict(tag='SALSEO',title='Linchamiento en casa',text='La mecha prendió aquí en mayo de 1520: los segovianos ahorcaron a su propio procurador, Rodrigo de Tordesillas, por votar en las Cortes el impuesto que pedía Carlos I. Volver a casa con el sí al rey no salió gratis.'),dict(tag='SALSEO',title='Casado con la nieta del rabino',text='Spoiler de la judería: Bravo se casó en segundas nupcias con María Coronel, nieta del gran rabino Abraham Seneor. Su suegro, Íñigo López Coronel, le dejó sus bienes. La familia del rabino acabó en el bando comunero.'),
         dict(tag='SALSEO',title='El rey guiri',text='Carlos I llegó de Flandes casi sin hablar castellano y con consejeros flamencos que se repartían cargos. Castilla estalló en 1520.'),
         dict(tag='FECHA',title='23-24 de abril de 1521',text='Los comuneros pierden en Villalar y al día siguiente decapitan a Bravo, Padilla y Maldonado.'),
         dict(tag='LEYENDA',title='Última frase',text='Cuando el pregonero lo llamó traidor, Bravo le gritó que mentía. Se cuenta así, aunque las versiones varían.',legend='Tradición'),
         dict(tag='DATO',title='Torres de presumir',text='El torreón de Lozoya, torre defensiva del siglo XIV, es de cuando los linajes segovianos se peleaban entre sí y cada familia quería su torre para atrincherarse.')],
  timeline=[dict(y='1520',e='Estalla la revuelta comunera'),dict(y='1521',e='Derrota en Villalar y ejecución'),dict(y='1921-22',e='Estatua de Aniceto Marinas por el IV centenario (inaugurada en 1922)')]),
 dict(id='corpus',skip='vedlo por fuera y id a Machado, que cierra a las 14:30',n='5',short='Corpus Christi',name='Corpus Christi (antigua sinagoga)',zone='Calle Real',time='13:38',stay=10,lat=40.94921,lon=-4.12404,gq='Iglesia del Corpus Christi, Segovia',alert='Cierra 14:15 · 1 € · rápido, Machado a las 14:00',
  hook='Una sinagoga que parece mezquita y acabó siendo iglesia por un "milagro" muy conveniente.',audio='audio/05.mp3',dur=58,
  images=[img('corpus','La entrada del Corpus Christi en la calle Real'),img('sinagoga','Capitel de piñas de la antigua sinagoga: buscadlo dentro')],
  look='Los arcos de herradura y las piñas talladas de los capiteles. Y el torno de las monjas, con dulces.',
  facts=[dict(tag='SALSEO',title='Un obispo con muchas sospechas',text='El obispo Juan de Tordesillas mandó detener a varios judíos, entre ellos Meir Alguadés, médico de Enrique III, y dos de los acusados más destacados fueron ejecutados. Encima, los acusó de sobornar a su cocinero para envenenarle.'),dict(tag='DATO',title='La Catorcena',text='El primer domingo de septiembre Segovia celebra la Catorcena, que recuerda el supuesto milagro de 1410. ¿El nombre? Las 14 parroquias históricas de la ciudad se turnan para organizarla.'),
         dict(tag='FECHA',title='1410',text='La comunidad judía pierde su Sinagoga Mayor tras una acusación de profanación de una hostia.'),
         dict(tag='MITO',title='La hostia voladora',text='Según la tradición, la echaron en agua hirviendo y quedó flotando en el aire mientras temblaban los muros. Los historiadores lo ven como una acusación inventada, típica de la Europa medieval.',legend='Tradición'),
         dict(tag='DATO',title='Incendio de 1899',text='El fuego dejó el edificio casi destruido: buena parte de lo que veis es una reconstrucción posterior.'),
         dict(tag='TIP',title='Dulces de clausura',text='Las clarisas venden dulces caseros por el torno. Buen tentempié antes de comer.')],
  numbers=[dict(v='1',u='€',l='entrada'),dict(v='1410',l='acusación y confiscación (fecha tradicional)')]),
 dict(id='machado',skip='última entrada a las 14:15: id directos',n='6',short='Casa de Machado',name='Casa-Museo de Antonio Machado',zone='San Esteban',time='13:56',stay=25,lat=40.95160,lon=-4.12580,gq='Casa-Museo de Antonio Machado, Calle Desamparados 5, Segovia',alert='Última entrada 14:00',
  hook='La pensión del poeta y el romance secreto que da nombre a vuestra estación.',audio='audio/06.mp3',dur=66,
  images=[img('machado-casa','El patio de la antigua pensión de la calle Desamparados'),img('machado-sorolla','Antonio Machado retratado por Sorolla en 1917',year='1917')],
  look='La habitación: la cama de hierro, la mesa y la estufa de petróleo donde escribía de noche.',
  facts=[dict(tag='SALSEO',title='Hotel Comercio, 1928',text='Se conocieron el 2 de junio de 1928 en el Hotel Comercio de Segovia. Él, viudo, tenía 52 años; ella, casada y con hijos, 38. Se veían a escondidas, sobre todo en Madrid.'),dict(tag='FAMOSOS',title='Académico desde la pensión',text='En 1927, viviendo en esta habitación, Machado fue elegido miembro de la Real Academia Española. Nunca leyó su discurso de ingreso, así que jamás ocupó el sillón.'),
         dict(tag='SALSEO',title='Guiomar',text='En 1928 Machado se enamora de Pilar de Valderrama, poeta y casada. Se ven a escondidas y él la llama Guiomar en sus versos.'),
         dict(tag='DATO',title='Vuestra estación',text='La estación de AVE Segovia-Guiomar lleva el nombre de la musa secreta del poeta.'),
         dict(tag='FECHA',title='1919-1932',text='Casi trece años en esta pensión, desde noviembre de 1919, dando clases de francés en el instituto.'),
         dict(tag='FAMOSOS',title='«Sí, soy Guiomar»',text='Pilar de Valderrama dio su versión en «Sí, soy Guiomar», publicado en 1981, dos años después de morir. Según ella, todo fue platónico; los expertos aún lo discuten.')],
  numbers=[dict(v='13',l='inviernos viviendo aquí'),dict(v='1928',l='conoce a Guiomar')],
  timeline=[dict(y='1919',e='Machado llega a Segovia'),dict(y='1928',e='Conoce a Pilar de Valderrama'),dict(y='1932',e='Se traslada a Madrid'),dict(y='2007',e='Abre la estación Segovia-Guiomar')]),
 dict(id='comida',skip='pedid la cuenta con el postre',n='C',short='Comida',name='Comida: La Cueva de San Esteban',kind='food',zone='San Esteban',time='14:25',stay=75,lat=40.95135,lon=-4.12470,gq='La Cueva de San Esteban, Calle Valdeláguila 15, Segovia',alert='Reservad ya',
  hook='Bodega-cueva de piedra con cocina segoviana de verdad y precios de barrio.',audio='audio/12.mp3',dur=56,
  images=[img('sanesteban','La torre de San Esteban, a dos pasos del restaurante, con la sierra nevada al fondo')],
  info=[dict(t='La Cueva de San Esteban',badge='PLAN A',bc='hot',p='Calle Valdeláguila 15, junto a la plaza de San Esteban. Tel. 921 460 982. Unos 22-32 € por persona. Solo 32 plazas: llamad para reservar a las 14:30.',ul=['Judiones de La Granja para compartir','Ración de cochinillo asado','Solomillo con salsa de grosellas','Leche frita de postre']),
        dict(t='El Sitio',badge='PLAN B · TAPAS',p='Calle Infanta Isabel 9, la calle de los bares que sale de la Plaza Mayor. Tel. 921 46 09 96. Unos 15-20 € tapeando. Abierto el domingo de 12:00 a 24:00, sin reserva en barra.',ul=['Caña o vino con su tapa','Timbal de berenjena','Cochinillo en el comedor de arriba']),
        dict(t='Mesón Don Jimeno',badge='PLAN C',p='Calle Daoíz 15, camino del Alcázar. Menú con cochinillo de segundo por unos 24 €. Pequeño: reservad.'),
        dict(t='Postre: ponche segoviano',p='Bizcocho, crema, mazapán y azúcar tostada en rombos. Pastelería Limón y Menta (Isabel la Católica 2, junto a la Plaza Mayor) o Pastelería Acueducto (calle Cervantes) a la vuelta.')],
  facts=[dict(tag='DATO',title='Guiño de calendario',text='La Gaceta de Madrid publicó la declaración de San Esteban como Monumento Nacional un 13 de diciembre de 1896: el mismo día en que, 422 años antes, Isabel se proclamó reina en la Plaza Mayor.'),dict(tag='DATO',title='Torre desmontable',text='A principios del siglo XX la torre de San Esteban se desmontó y se volvió a montar con un románico algo pasado de rosca: casi todos los capiteles se tallaron de nuevo. Su chapitel de pizarra se cambió después por el remate cerámico actual.')],
  look='La torre de San Esteban, a la vuelta de la esquina: unos 53 metros, presume de ser la más alta del románico español. La apodan «reina de las torres bizantinas», aunque es románica pura.'),
 dict(id='plazamayor',skip='foto rápida y a la Catedral',n='7',short='Plaza Mayor',name='Plaza Mayor y San Miguel',zone='Plaza Mayor',time='15:45',stay=15,lat=40.95029,lon=-4.12369,gq='Plaza Mayor, Segovia',
  hook='Aquí Isabel se proclamó reina sin esperar a su marido.',audio='audio/07.mp3',dur=72,
  images=[img('proclamacion-1847','La proclamación de Isabel en Segovia, grabado de 1847',year='1847'),img('plaza-mayor','La Plaza Mayor hoy'),img('sanmiguel','San Miguel, la iglesia reconstruida tras el derrumbe'),img('segovia-1975','La plaza en 1975',year='1975')],
  look='La iglesia de San Miguel, en un lateral de la plaza. En su fachada hay relieves románicos reaprovechados de la iglesia vieja, ante la que se proclamó Isabel.',
  facts=[dict(tag='DATO',title='¿Tanto monta, Isabel como Fernando?',text='Pues no: «tanto monta» era el lema personal de Fernando y alude a Alejandro Magno y el nudo gordiano (tanto monta cortar como desatar). Lo de «Isabel como Fernando» es una coletilla popular posterior.'),dict(tag='SALSEO',title='Reina a los 23',text='Isabel tenía 23 años y su hermano Enrique IV había muerto en Madrid solo dos días antes. Fernando no llegó a Segovia hasta el 2 de enero de 1475, y hubo tira y afloja sobre quién mandaba.'),
         dict(tag='SALSEO',title='Reina sin el marido',text='13 de diciembre de 1474: Isabel se proclama reina de Castilla aquí. Fernando estaba en Aragón y se enteró después.'),
         dict(tag='SALSEO',title='La espada desnuda',text='Delante de ella desfiló Gutierre de Cárdenas con la espada desnuda en alto, símbolo de la justicia real. Según el cronista Alonso de Palencia, a algunos les pareció un exceso en una mujer.'),
         dict(tag='FECHA',title='Concordia de Segovia, 1475',text='Firmada el 15 de enero, repartió el poder: Fernando sería rey y firmarían juntos, pero la heredera de Castilla seguía siendo ella.'),
         dict(tag='DATO',title='Iglesia nueva',text='La San Miguel de 1474 se hundió en el siglo XVI y se reconstruyó unos metros más atrás.')],
  ba=dict(before='img/segovia-1975.webp',after='img/plaza-mayor.webp',by='1975',ay='Hoy',cap='La Plaza Mayor en 1975 y hoy, ya peatonal.'),
  timeline=[dict(y='1474',e='Isabel se proclama reina'),dict(y='1475',e='Concordia de Segovia'),dict(y='1532',e='Se hunde la iglesia vieja'),dict(y='1536',e='Se decide levantar la nueva San Miguel')]),
 dict(id='catedral',skip='vedla por fuera y seguid',n='8',short='Catedral',name='Catedral de Segovia',zone='Plaza Mayor',time='16:05',stay=40,lat=40.95024,lon=-4.12522,gq='Catedral de Segovia',alert='Domingo hasta 18:30',
  hook='La última gran catedral gótica de España: nació pasada de moda y le salió espectacular.',audio='audio/08.mp3',dur=62,
  images=[img('catedral','La catedral iluminada de noche'),img('claustro','El claustro que viajó piedra a piedra desde la catedral vieja'),img('catedral-torre','La catedral y la sierra de Guadarrama desde la torre del Alcázar')],
  look='Dentro: el claustro, traído piedra a piedra desde la catedral vieja, y la tumba del infante don Pedro.',
  facts=[dict(tag='DATO',title='243 años de obras',text='Primera piedra el 8 de junio de 1525, con trazas de Juan Gil de Hontañón, y consagración el 16 de julio de 1768: 243 años de paciencia. Resultado: unos 105 m de largo y 33 de alto en la nave central.'),dict(tag='SALSEO',title='María del Salto',text='En el claustro reposa María del Salto. Según la tradición, era una judía acusada de adulterio a la que despeñaron desde la Peña Grajera en el siglo XIII. Invocó a la Virgen de la Fuencisla, sobrevivió y se convirtió.'),
         dict(tag='FECHA',title='1525',text='Se empieza la nueva catedral porque la vieja, junto al Alcázar, quedó destrozada en la guerra de los Comuneros.'),
         dict(tag='DATO',title='Claustro viajero',text='El claustro de la catedral vieja se desmontó y se volvió a montar aquí, pieza a pieza.'),
         dict(tag='CIFRA',title='Casi 90 metros',text='Su torre ronda los 88 m. Arriba vivía el campanero: se dice que era la casa más alta de España.'),
         dict(tag='LEYENDA',title='El infante y la niñera',text='Se cuenta que un bebé real cayó desde una ventana del Alcázar y que su niñera se lanzó tras él.',legend='Leyenda')],
  numbers=[dict(v='88',u='m',l='altura de la torre'),dict(v='1525',l='inicio de las obras'),dict(v='4',u='€',l='entrada aprox.')],
  chart=dict(title='Torres que dan vértigo',max=100,rows=[dict(l='Catedral',v=88,t='88 m',hl=True),dict(l='Acueducto',v=28,t='28 m'),dict(l='Torre Juan II',v=80,t='~80 m s. río',)],note='La torre de Juan II del Alcázar, medida desde el valle del Eresma. Valores aproximados.')),
 dict(id='juderia',skip='saltad la Judería y subid por la calle Daoíz al Alcázar',n='9',short='Judería',name='Judería y Puerta de San Andrés',zone='Judería',time='16:55',stay=20,lat=40.94991,lon=-4.12713,via=[-4.12484,40.94943],gq='Puerta de San Andrés, Segovia',
  hook='El rabino que se bautizó con los Reyes Católicos de padrinos.',audio='audio/09.mp3',dur=58,
  images=[img('sanandres-1865','La Puerta de San Andrés en un grabado de 1865',year='1865'),img('murallas-juderia','La muralla que cerraba la judería por el sur'),img('juderia-calle','Placa de la calle de la Judería Vieja'),img('cementerio-judio','El Pinarillo, el antiguo cementerio judío, al otro lado del valle')],
  look='Desde el mirador de la Puerta de San Andrés, al otro lado del valle: El Pinarillo, el antiguo cementerio judío.',
  facts=[dict(tag='FAMOSOS',title='El médico de la casa',text='Tras la muerte de Seneor, su casa de la calle Judería Vieja (hoy Centro Didáctico) fue hogar de Andrés Laguna, el médico humanista segoviano más famoso del siglo XVI, de familia conversa.'),dict(tag='DATO',title='Arco del Socorro',text='La Puerta de San Andrés, documentada ya en 1120, también se llama Arco del Socorro por la Virgen de su hornacina. De las puertas de la muralla solo quedan tres: San Andrés, Santiago y San Cebrián.'),
         dict(tag='SALSEO',title='Padrinos reales',text='Abraham Seneor, rabino mayor de Castilla y financiero de Isabel, se bautizó en 1492 con los Reyes Católicos como padrinos.'),
         dict(tag='DATO',title='Nuevo nombre',text='Pasó a llamarse Fernán Pérez Coronel. Rondaba los 80 años y murió en Segovia al año siguiente, en 1493.'),
         dict(tag='TIP',title='Domingo',text='El Centro Didáctico de la Judería cierra el domingo por la tarde: ved la fachada y bajad al mirador.')],
  timeline=[dict(y='1412',e='Se obliga a los judíos a vivir en la judería'),dict(y='1492',e='Decreto de expulsión'),dict(y='1492',e='Seneor se bautiza')]),
 dict(id='alcazar',skip='saltad la torre de Juan II',n='10',short='Alcázar',name='Alcázar de Segovia',zone='Zona alta',time='17:30',stay=75,lat=40.95229,lon=-4.13141,gq='Alcázar de Segovia',alert='Cierra 19:00-20:00 (confirmad) · Torre a hora fija',
  hook='El castillo-barco que media internet relaciona con Disney.',audio='audio/10.mp3',dur=69,
  images=[img('alcazar-otono','El Alcázar sobre el valle en otoño'),img('alcazar-2017','La proa del Alcázar al atardecer'),img('alcazar-1900','Fotocromo de hacia 1890-1900',year='c. 1900')],
  look='En la Sala del Cordón, el cordón franciscano que rodea el techo. Y la torre de Juan II: 152 escalones.',
  facts=[dict(tag='SALSEO',title='¿Fueron los cadetes?',text='El 6 de marzo de 1862 el fuego arrasó tejados y techos mudéjares. Circula que lo provocaron los propios cadetes para que no trasladaran su academia, pero no hay ni una prueba. La restauración no arrancó hasta 1882.'),dict(tag='FAMOSOS',title='Los héroes vuelven a casa',text='Por el Real Colegio de Artillería pasaron Daoíz y Velarde, los capitanes del 2 de mayo de 1808. Su monumento en la plaza, frente a su antigua academia, es de Aniceto Marinas, el mismo escultor del Juan Bravo.'),
         dict(tag='MITO',title='¿Inspiró a Disney?',text='No hay ningún documento que lo pruebe. El castillo de Disney se parece más a Neuschwanstein, en Baviera.',legend='Mito muy extendido'),
         dict(tag='FECHA',title='Incendio de 1862',text='El fuego destruyó tejados e interiores. Las agujas de pizarra son una reconstrucción de finales del siglo XIX.'),
         dict(tag='LEYENDA',title='Alfonso X y el rayo',text='El rey dijo que, de haber estado en la Creación, habría dado consejos a Dios. Cayó un rayo y se puso un cordón de penitencia.',legend='Leyenda'),
         dict(tag='SALSEO',title='Boda con la sobrina',text='En noviembre de 1570 Felipe II se casó en Segovia con su cuarta esposa, Ana de Austria, hija de su hermana María: su sobrina. Él, 43 años; ella, 21.'),
         dict(tag='DATO',title='Escuela de cadetes',text='Desde 1764 fue sede del Real Colegio de Artillería.')],
  numbers=[dict(v='152',l='escalones de la torre de Juan II'),dict(v='1862',l='año del gran incendio'),dict(v='~10',u='€',l='entrada completa')],
  ba=dict(before='img/alcazar-despues.webp',after='img/alcazar-otono.webp',by='Tras 1862',ay='Hoy',cap='Grabado del Alcázar tras el incendio de 1862, sin sus tejados, y el Alcázar hoy con las agujas reconstruidas.'),
  timeline=[dict(y='s. XII',e='Primer alcázar documentado'),dict(y='1474',e='Isabel sale de aquí a proclamarse reina'),dict(y='1570',e='Boda de Felipe II y Ana de Austria'),dict(y='1764',e='Real Colegio de Artillería'),dict(y='1862',e='Incendio'),dict(y='fin s. XIX',e='Reconstrucción de las cubiertas')]),
 dict(id='vuelta',n='B',short='Bus 19:40',name='Bajada al Acueducto y bus 11',kind='bus',zone='Vuelta',time='19:40',stay=0,lat=40.94715,lon=-4.11705,gq='Plaza de Artillería, Segovia',alert='Salid del Alcázar 19:00 · en la parada 19:25',skip='taxi en la Plaza Mayor o el Azoguejo',
  hook='Veinticinco minutos cuesta abajo por la calle Real con la puesta de sol, y el bus 11 de las 19:40 a Guiomar.',audio='audio/11.mp3',dur=59,
  deps=dict(title='Bus 11 · Acueducto → Guiomar',note=BUS_NOTE_BACK,list=BUS_BACK),
  images=[img('acueducto-noche','El acueducto iluminado al anochecer')],
  info=[dict(t='Autobús línea 11 · Acueducto → Guiomar',badge='19:40',bc='ok',p='Cabecera Acueducto 3, en la plaza de Artillería, junto al acueducto. Llega a Guiomar hacia las 19:54, 24 min antes de vuestro Avant de las 20:18. Va lleno de gente que vuelve a Madrid: estad en la parada a las 19:25. Si queréis ir sobrados, el de las 19:10. El de las 20:00 ya no sirve.'),
        dict(t='Plan B: taxi',badge='SI EL BUS VA LLENO',p='Parada de taxis en el Azoguejo, al lado. Unos 11-12 € en domingo y 10-12 min hasta Guiomar.'),
        dict(t='Comprobad la hora en directo',p='App «Urbanos de Segovia» (Avanza), Moovit o el panel de la parada. Atención al cliente de Avanza:',tel='900 925 303'),
        dict(t='No hay bus desde la zona alta',p='Ninguna línea va directa de la Plaza Mayor o el Alcázar a la estación. Lo más rápido es bajar andando (20-25 min) o taxi.')],
  look='El acueducto con la última luz: el sol se pone a las 19:43.'),
 dict(id='estacion',n='T',short='Tren 20:18',name='Estación Guiomar · Avant 20:18',kind='train',zone='Vuelta',time='19:55',stay=23,lat=40.91010,lon=-4.09490,gq='Estación de Segovia-Guiomar',alert='Avant 08198 · 20:18 · coche 6, asiento 66',
  hook='Llegad con margen: el AVE tiene control de equipajes y el acceso al andén cierra unos minutos antes.',
  images=[img('guiomar-a','La estación de Segovia-Guiomar'),img('guiomar-b','Andenes con la sierra al fondo')],
  info=[dict(t='Vuestro tren de vuelta',badge='20:18',bc='ok',p='Avant 08198 · Segovia-Guiomar 20:18 → Chamartín 20:46. Coche 006, asiento 066. El billete está en la Wallet.'),
        dict(t='En la estación',ul=['Pasad el control de equipaje nada más llegar','El acceso al tren cierra unos 2 minutos antes de la salida','Hay cafetería y máquinas si queréis algo para el viaje']),
        dict(t='Plan B si perdéis el bus',p='Taxi desde la Plaza Mayor o el Azoguejo: unos 11-12 € en domingo y 10-12 min. Si a las 19:40 el bus va lleno, id directos a la parada de taxis del Azoguejo.')],
  facts=[dict(tag='TIP',title='Para el tren',text='Si comprasteis ponche segoviano, este es el momento: aguanta bien el viaje.')]),
]
meta=dict(arrive='12:32',train='20:18',returnBus='19:40',walkDown=40)
planInfo=[dict(t='Vuestros trenes',ul=['Ida: Avant 08129 · Chamartín 12:05 → Guiomar 12:32 · coche 007, asiento 155','Vuelta: Avant 08198 · Guiomar 20:18 → Chamartín 20:46 · coche 006, asiento 066']),
 dict(t='Ida: bus 11 desde Guiomar',badge='12:40 · 12:45',bc='ok',p='Horario de domingo según Moovit. El siguiente no sale hasta las 13:50, así que salid rápido del andén. 15 min hasta el Acueducto. 2,25 € con tarjeta, móvil o efectivo. La línea 12 también os vale.'),
 dict(t='Vuelta: bus 11 desde el Acueducto',badge='19:40',bc='ok',p='Parada Acueducto 3 (plaza de Artillería). Estad allí a las 19:25 porque se llena. Llegáis a Guiomar hacia las 19:54, con 24 min para el Avant de las 20:18. Si queréis ir sobrados, el de las 19:10. El de las 20:00 ya no sirve. Plan B: taxi en el Azoguejo.'),
 dict(t='Horarios del domingo',ul=['Corpus Christi: hasta 14:15 (1 €)','Casa de Machado: hasta 14:30, última entrada 14:00','Catedral: 13:30-18:30 (unos 4 €)','Alcázar: desde las 10:00, cierre a las 19:00 o 20:00 según la fuente (confirmadlo) (unos 10 € con torre)','Centro de la Judería: cerrado por la tarde']),
 dict(t='Puesta de sol 19:43',p='Mediados de octubre: unos 18 °C de máxima, pero refresca mucho al caer el sol. Chaqueta y calzado cómodo: hay adoquines y unos 60 m de desnivel.'),
 dict(t='Reservad la comida ahora',badge='IMPORTANTE',bc='hot',p='Es puente del Pilar. La Cueva de San Esteban tiene 32 plazas: 921 460 982.')]
credits='Fotos: Wikimedia Commons (autores en commons.wikimedia.org). Mapa: Overture Maps Foundation y colaboradores de OpenStreetMap. Voz: ElevenLabs. Horarios y precios orientativos; confirmadlos el mismo día.'
# routing
G=pickle.load(open(SP+'map/graph.pkl','rb'))
nodes=list(G.nodes)
def hav(a,b):
    R0=6371000; la1,lo1,la2,lo2=map(math.radians,[a[1],a[0],b[1],b[0]])
    return 2*R0*math.asin(math.sqrt(math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2))
def near(lon,lat): return min(nodes,key=lambda n:(n[0]-lon)**2+((n[1]-lat)*1.3)**2)
GD=pickle.load(open(SP+'map/graph_drive.pkl','rb'))
dnodes=list(GD.nodes)
def dnear(lon,lat): return min(dnodes,key=lambda n:(n[0]-lon)**2+((n[1]-lat)*1.3)**2)
BUS_STOP=(-4.11705,40.94715)
def drive(p1,p2):
    a,b=dnear(*p1),dnear(*p2); pth=nx.shortest_path(GD,a,b,weight='w'); m=sum(GD[u][v]['d'] for u,v in zip(pth,pth[1:]))
    return [[round(x,6),round(y,6)] for x,y in pth], m
legs=[]
for a,b in zip(stops,stops[1:]):
    if a['id']=='guiomar':
        c1,m1=drive((a['lon'],a['lat']),BUS_STOP)
        na,nb=near(*BUS_STOP),near(b['lon'],b['lat']); pw=nx.shortest_path(G,na,nb,weight='w'); m2=sum(G[u][v]['d'] for u,v in zip(pw,pw[1:]))
        coords=[[a['lon'],a['lat']]]+c1+[[round(x,6),round(y,6)] for x,y in pw]+[[b['lon'],b['lat']]]
        legs.append(dict(coords=coords,m=int(round((m1+m2)/10)*10),min=17,mode='bus',note='bus 11 (15 min) + 2 min a pie')); print('bus out',int(m1),int(m2)); continue
    if b['id']=='estacion':
        c1,m1=drive((a['lon'],a['lat']),(b['lon'],b['lat']))
        legs.append(dict(coords=[[a['lon'],a['lat']]]+c1+[[b['lon'],b['lat']]],m=int(round(m1/10)*10),min=15,mode='bus',note='bus 11')); print('bus back',int(m1)); continue
    na,nb=near(a['lon'],a['lat']),near(b['lon'],b['lat'])
    try:
        if b.get('via'):
            nv=near(*b['via']); p1=nx.shortest_path(G,na,nv,weight='w'); p2=nx.shortest_path(G,nv,nb,weight='w'); p=p1+p2[1:]
        else:
            p=nx.shortest_path(G,na,nb,weight='w')
        m=sum(G[u][v]['d'] for u,v in zip(p,p[1:]))
        coords=[[a['lon'],a['lat']]]+[[round(x,6),round(y,6)] for x,y in p]+[[b['lon'],b['lat']]]
    except Exception as e:
        coords=[[a['lon'],a['lat']],[b['lon'],b['lat']]]; m=hav(coords[0],coords[1])*1.3
    mins=max(2,round(m/65))
    legs.append(dict(coords=coords,m=int(round(m/10)*10),min=mins,mode='walk'))
    print(a['id'],'->',b['id'],int(m),'m',mins,'min')
legs[-2]['note']='casi todo cuesta abajo'
tour=dict(stops=stops,legs=legs,meta=meta,planInfo=planInfo,credits=credits)
t=open(SP+'template.html').read()
css=open(SP+'map/package/dist/maplibre-gl.css').read()
WEB='https://raw.githack.com/homerojimenez/App-visitas/HEAD/index.html'
t=t.replace('/*__MLCSS__*/',css).replace('/*__DATA__*/null',json.dumps(tour,ensure_ascii=False)).replace('/*__WEBURL__*/',WEB)
open(OUT+'artifact.html','w').write(t)
head='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1a6cf0"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Segovia"><meta name="apple-mobile-web-app-status-bar-style" content="default"><link rel="apple-touch-icon" href="icon-180.png"><link rel="icon" type="image/png" href="icon-192.png"><link rel="manifest" href="manifest.webmanifest"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open(OUT+'index.html','w').write(head+t.replace('<meta charset="utf-8">\n','',1)+'</body></html>')
os.makedirs(OUT+'fonts/NotoReg',exist_ok=True); shutil.copy(SP+'map/glyph0.pbf',OUT+'fonts/NotoReg/0-255.ttf')
shutil.copy(SP+'map/map.json',OUT+'map.json')
os.makedirs(OUT+'img',exist_ok=True); os.makedirs(OUT+'audio',exist_ok=True)
for f in os.listdir(SP+'img'): shutil.copy(SP+'img/'+f,OUT+'img/'+f)
for f in os.listdir(SP+'audio'):
    shutil.copy(SP+'audio/'+f,OUT+'audio/'+('00.mp3' if f.startswith('00') else f))
print('ok', os.path.getsize(OUT+'index.html'))
