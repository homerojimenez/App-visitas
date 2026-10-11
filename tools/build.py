import json, math, pickle, os, shutil, networkx as nx
SP='/tmp/claude-0/-home-user-App-visitas/337edbc6-130b-5668-97df-f033ed5dc189/scratchpad/'
OUT='/home/user/App-visitas/'
W='Wikimedia Commons'
def img(f,cap,credit=W,year=None): return {'src':'img/'+f+'.webp','cap':cap,'credit':credit,**({'year':year} if year else {})}
stops=[
 dict(id='acueducto',n='1',short='Acueducto',name='Acueducto y Azoguejo',zone='Zona baja',time='13:00',stay=20,lat=40.94795,lon=-4.11790,gq='Plaza del Azoguejo, Segovia',
  hook='Casi 2.000 años en pie, 20.000 bloques de granito y ni una gota de cemento.',audio='audio/01.mp3',dur=59,
  images=[img('acueducto-arcos','Los arcos desde abajo: puro equilibrio'),img('azoguejo','La vista desde la calle Real hacia el Azoguejo'),img('acueducto-noche','De noche se ilumina y el granito se vuelve dorado'),img('acueducto-antiguo','El acueducto en una fotografía del siglo XIX',year='s. XIX')],
  look='Los agujeritos en los bloques: ahí se enganchaban las tenazas para subirlos. Y arriba, las hornacinas con figuras.',
  facts=[dict(tag='CIFRA',title='Sin cemento',text='Unos 20.400 bloques de granito sin argamasa. Se sostienen solo por el peso y la geometría de los arcos.'),
         dict(tag='LEYENDA',title='El diablo y la aguadora',text='Una aguadora vendió su alma al diablo para que le subiera el agua en una noche. Cantó el gallo cuando faltaba una piedra y se libró.',legend='Leyenda popular'),
         dict(tag='DATO',title='Coches bajo los arcos',text='Durante décadas el tráfico pasó por debajo, autobuses incluidos. Las vibraciones y la contaminación obligaron a cortarlo a principios de los 90.'),
         dict(tag='FECHA',title='Patrimonio de la Humanidad',text='En 1985 la UNESCO declaró Patrimonio Mundial la ciudad vieja de Segovia junto a su acueducto.'),
         dict(tag='FAMOSOS',title='El mesón de las fotos',text='A los pies del acueducto está el Mesón de Cándido, donde el cochinillo se corta con un plato. La casa presume de una pared llena de fotos con famosos.')],
  numbers=[dict(v='28',u='m',l='altura máxima, aquí en el Azoguejo'),dict(v='167',l='arcos'),dict(v='~20.400',l='bloques de granito'),dict(v='15',u='km',l='desde la sierra (río Frío)')],
  chart=dict(title='¿Cómo de alto es?',max=30,rows=[dict(l='Acueducto',v=28,t='28 m',hl=True),dict(l='Edificio 9 plantas',v=27,t='27 m'),dict(l='Árbol grande',v=15,t='15 m'),dict(l='Autobús',v=3.2,t='3 m')],note='Comparativa aproximada.'),
  ba=dict(before='img/acueducto-1838.webp',after='img/azoguejo.webp',by='1838',ay='Hoy',cap='En 1838 el Azoguejo era un mercado con casas pegadas a los pilares. Hoy la plaza está despejada y peatonal.'),
  timeline=[dict(y='s. I-II',e='Roma levanta el acueducto'),dict(y='1072',e='Los almorávides destruyen 36 arcos'),dict(y='1484',e='Los Reyes Católicos los reconstruyen'),dict(y='1985',e='Patrimonio de la Humanidad'),dict(y='1990s',e='Se corta el tráfico bajo los arcos')]),
 dict(id='mirador',n='2',short='Mirador',name='Mirador del Postigo del Consuelo',zone='Zona baja',time='13:22',stay=6,lat=40.94868,lon=-4.11902,gq='Postigo del Consuelo, Segovia',
  hook='Subid las escaleras pegadas al acueducto: aquí está la foto de pareja.',audio='audio/02.mp3',dur=58,
  images=[img('acueducto-08','El acueducto entero desde lo alto, con el Azoguejo abajo'),img('acueducto-arcos','Las dos filas de arcos')],
  look='El canal por donde corría el agua, en lo alto del acueducto, casi a la altura de vuestros ojos.',
  facts=[dict(tag='DATO',title='Un sudoku romano',text='La inscripción de bronce desapareció, pero Géza Alföldy reconstruyó el texto a partir de los agujeros de los clavos.'),
         dict(tag='CIFRA',title='Pendiente mínima',text='El agua bajaba por gravedad con una pendiente casi imperceptible a lo largo de unos 15 km.'),
         dict(tag='TIP',title='Foto',text='Poneos de espaldas a la barandilla con el acueducto en diagonal: sale entero con la ciudad nueva al fondo.')],
  numbers=[dict(v='2',l='filas de arcos en la parte alta'),dict(v='~1',u='%',l='de pendiente media del canal')]),
 dict(id='picos',n='3',short='Casa de los Picos',name='Casa de los Picos',zone='Calle Real',time='13:33',stay=5,lat=40.94913,lon=-4.12005,gq='Casa de los Picos, Segovia',
  hook='Más de 600 puntas de diamante en una fachada. ¿Ostentación o algo más?',audio='audio/03.mp3',dur=52,
  images=[img('picos','La fachada de los picos en la calle Juan Bravo')],
  look='Mirad la fachada en diagonal desde la esquina: los picos hacen un efecto óptico con la luz.',
  facts=[dict(tag='CIFRA',title='617 picos',text='Es la cifra que se suele dar: más de seiscientos bloques tallados en punta de diamante.'),
         dict(tag='MITO',title='¿Por qué los picos?',text='Hay varias versiones: ostentación de una familia noble, defensa junto a la muralla o una forma de acallar habladurías. Ninguna está probada.',legend='Origen discutido'),
         dict(tag='DATO',title='Hoy, Escuela de Arte',text='Los alumnos de la Escuela de Arte y Superior de Diseño entran cada mañana bajo las seiscientas puntas.')],
  numbers=[dict(v='617',l='picos de granito'),dict(v='s. XV',l='época de la fachada')]),
 dict(id='sanmartin',n='4',short='Juan Bravo',name='Plaza de San Martín y Juan Bravo',zone='Calle Real',time='13:40',stay=8,lat=40.94975,lon=-4.12236,gq='Plaza de Medina del Campo, Segovia',
  hook='El rebelde que plantó cara a Carlos I y perdió la cabeza por ello.',audio='audio/04.mp3',dur=60,
  images=[img('juanbravo','Juan Bravo de noche, con la Casa del Siglo XV detrás'),img('sanmartin','San Martín y su galería porticada románica')],
  look='La estatua de Juan Bravo con el estandarte, y detrás la galería porticada de San Martín.',
  facts=[dict(tag='SALSEO',title='El rey guiri',text='Carlos I llegó de Flandes casi sin hablar castellano y con consejeros flamencos que se repartían cargos. Castilla estalló en 1520.'),
         dict(tag='FECHA',title='23-24 de abril de 1521',text='Los comuneros pierden en Villalar y al día siguiente decapitan a Bravo, Padilla y Maldonado.'),
         dict(tag='LEYENDA',title='Última frase',text='Cuando el pregonero lo llamó traidor, Bravo le gritó que mentía. Se cuenta así, aunque las versiones varían.',legend='Tradición'),
         dict(tag='DATO',title='Torres de presumir',text='El torreón de Lozoya es de cuando los linajes segovianos competían por la torre más alta.')],
  timeline=[dict(y='1520',e='Estalla la revuelta comunera'),dict(y='1521',e='Derrota en Villalar y ejecución'),dict(y='1921',e='Se inaugura la estatua en el IV centenario')]),
 dict(id='corpus',n='5',short='Corpus Christi',name='Corpus Christi (antigua sinagoga)',zone='Calle Real',time='13:50',stay=12,lat=40.94998,lon=-4.12392,gq='Iglesia del Corpus Christi, Segovia',alert='Cierra 14:15 · 1 €',
  hook='Una sinagoga que parece mezquita y acabó siendo iglesia por un "milagro" muy conveniente.',audio='audio/05.mp3',dur=58,
  images=[img('corpus','La entrada del Corpus Christi en la calle Real'),img('sinagoga','Capitel de piñas de la antigua sinagoga: buscadlo dentro')],
  look='Los arcos de herradura y las piñas talladas de los capiteles. Y el torno de las monjas, con dulces.',
  facts=[dict(tag='FECHA',title='1410',text='La comunidad judía pierde su Sinagoga Mayor tras una acusación de profanación de una hostia.'),
         dict(tag='MITO',title='La hostia voladora',text='Según el relato de la época, la hostia escapó volando. Los historiadores lo ven como una acusación inventada, típica de la Europa medieval.',legend='Relato de la época'),
         dict(tag='DATO',title='Incendio de 1899',text='Un fuego arrasó gran parte del interior. Lo que veis es una reconstrucción muy fiel.'),
         dict(tag='TIP',title='Dulces de clausura',text='Las clarisas venden dulces caseros por el torno. Buen tentempié antes de comer.')],
  numbers=[dict(v='1',u='€',l='entrada'),dict(v='1410',l='pasa de sinagoga a iglesia')]),
 dict(id='machado',n='6',short='Casa de Machado',name='Casa-Museo de Antonio Machado',zone='San Esteban',time='14:03',stay=25,lat=40.95180,lon=-4.12410,gq='Casa-Museo de Antonio Machado, Calle Desamparados 5, Segovia',alert='Última entrada 14:15',
  hook='La pensión del poeta y el romance secreto que da nombre a vuestra estación.',audio='audio/06.mp3',dur=66,
  images=[img('machado-casa','El patio de la antigua pensión de la calle Desamparados'),img('machado-sorolla','Antonio Machado retratado por Sorolla en 1917',year='1917')],
  look='La habitación: la cama de hierro, la mesa y la estufa de petróleo donde escribía de noche.',
  facts=[dict(tag='SALSEO',title='Guiomar',text='En 1928 Machado se enamora de Pilar de Valderrama, poeta y casada. Se ven a escondidas y él la llama Guiomar en sus versos.'),
         dict(tag='DATO',title='Vuestra estación',text='La estación de AVE Segovia-Guiomar lleva el nombre de la musa secreta del poeta.'),
         dict(tag='FECHA',title='1919-1932',text='Doce años en esta pensión, dando clases de francés en el instituto.'),
         dict(tag='FAMOSOS',title='«Sí, soy Guiomar»',text='Pilar de Valderrama guardó el secreto durante décadas y lo confesó en un libro que se publicó tras su muerte.')],
  numbers=[dict(v='12',l='años viviendo aquí'),dict(v='1928',l='conoce a Guiomar')],
  timeline=[dict(y='1919',e='Machado llega a Segovia'),dict(y='1928',e='Conoce a Pilar de Valderrama'),dict(y='1932',e='Se traslada a Madrid'),dict(y='2007',e='Abre la estación Segovia-Guiomar')]),
 dict(id='comida',n='C',short='Comida',name='Comida: La Cueva de San Esteban',kind='food',zone='San Esteban',time='14:35',stay=75,lat=40.95196,lon=-4.12575,gq='La Cueva de San Esteban, Calle Valdeláguila 15, Segovia',alert='Reservad ya',
  hook='Bodega-cueva de piedra con cocina segoviana de verdad y precios de barrio.',
  images=[img('sanesteban','La torre de San Esteban, a dos pasos del restaurante, con la sierra nevada al fondo')],
  info=[dict(t='La Cueva de San Esteban',badge='PLAN A',bc='hot',p='Calle Valdeláguila 15, junto a la plaza de San Esteban. Tel. 921 460 982. Unos 22-32 € por persona. Solo 32 plazas: llamad para reservar a las 14:30.',ul=['Judiones de La Granja para compartir','Ración de cochinillo asado','Solomillo con salsa de grosellas','Leche frita de postre']),
        dict(t='El Sitio',badge='PLAN B · TAPAS',p='Calle Infanta Isabel 9, la calle de los bares que sale de la Plaza Mayor. Tel. 921 46 09 96. Unos 15-20 € tapeando. Abierto el domingo de 12:00 a 24:00, sin reserva en barra.',ul=['Caña o vino con su tapa','Timbal de berenjena','Cochinillo en el comedor de arriba']),
        dict(t='Mesón Don Jimeno',badge='PLAN C',p='Calle Daoíz 15, camino del Alcázar. Menú con cochinillo de segundo por unos 24 €. Pequeño: reservad.'),
        dict(t='Postre: ponche segoviano',p='Bizcocho, crema, mazapán y azúcar tostada en rombos. Pastelería Limón y Menta (Isabel la Católica 2, junto a la Plaza Mayor) o Pastelería Acueducto (calle Cervantes) a la vuelta.')],
  look='La torre de San Esteban, a la vuelta de la esquina: la llaman la reina de las torres románicas.'),
 dict(id='plazamayor',n='7',short='Plaza Mayor',name='Plaza Mayor y San Miguel',zone='Plaza Mayor',time='15:55',stay=15,lat=40.95060,lon=-4.12500,gq='Plaza Mayor, Segovia',
  hook='Aquí Isabel se proclamó reina sin avisar a su marido.',audio='audio/07.mp3',dur=65,
  images=[img('proclamacion-1847','La proclamación de Isabel en Segovia, grabado de 1847',year='1847'),img('plaza-mayor','La Plaza Mayor hoy'),img('sanmiguel','San Miguel, la iglesia reconstruida tras el derrumbe'),img('segovia-1975','La plaza en 1975',year='1975')],
  look='La iglesia de San Miguel, en un lateral de la plaza. La original, donde se proclamó Isabel, estaba un poco más adelante.',
  facts=[dict(tag='SALSEO',title='Reina sin el marido',text='13 de diciembre de 1474: Isabel se proclama reina de Castilla aquí. Fernando estaba en Aragón y se enteró después.'),
         dict(tag='SALSEO',title='La espada desnuda',text='Delante de ella desfiló un caballero con la espada desenvainada, símbolo de la justicia real. A Fernando no le hizo ninguna gracia.'),
         dict(tag='FECHA',title='Concordia de Segovia, 1475',text='El pacto que repartió el poder entre los dos. De ahí el «tanto monta, monta tanto».'),
         dict(tag='DATO',title='Iglesia nueva',text='La San Miguel de 1474 se hundió en el siglo XVI y se reconstruyó unos metros más atrás.')],
  ba=dict(before='img/segovia-1975.webp',after='img/plaza-mayor.webp',by='1975',ay='Hoy',cap='La Plaza Mayor en 1975 y hoy, ya peatonal.'),
  timeline=[dict(y='1474',e='Isabel se proclama reina'),dict(y='1475',e='Concordia de Segovia'),dict(y='1532',e='Se hunde la iglesia vieja'),dict(y='1558',e='Nueva San Miguel')]),
 dict(id='catedral',n='8',short='Catedral',name='Catedral de Segovia',zone='Plaza Mayor',time='16:15',stay=40,lat=40.94990,lon=-4.12560,gq='Catedral de Segovia',alert='Domingo hasta 18:30',
  hook='La última gran catedral gótica de España: nació pasada de moda y le salió espectacular.',audio='audio/08.mp3',dur=62,
  images=[img('catedral','La catedral iluminada de noche'),img('claustro','El claustro que viajó piedra a piedra desde la catedral vieja'),img('catedral-torre','La catedral y la sierra de Guadarrama desde la torre del Alcázar')],
  look='Dentro: el claustro, traído piedra a piedra desde la catedral vieja, y la tumba del infante don Pedro.',
  facts=[dict(tag='FECHA',title='1525',text='Se empieza la nueva catedral porque la vieja, junto al Alcázar, quedó destrozada en la guerra de los Comuneros.'),
         dict(tag='DATO',title='Claustro viajero',text='El claustro de la catedral vieja se desmontó y se volvió a montar aquí, pieza a pieza.'),
         dict(tag='CIFRA',title='Casi 90 metros',text='Su torre ronda los 88 m. Arriba vivía el campanero: se dice que era la casa más alta de España.'),
         dict(tag='LEYENDA',title='El infante y la niñera',text='Se cuenta que un bebé real cayó desde una ventana del Alcázar y que su niñera se lanzó tras él.',legend='Leyenda')],
  numbers=[dict(v='88',u='m',l='altura de la torre'),dict(v='1525',l='inicio de las obras'),dict(v='4',u='€',l='entrada aprox.')],
  chart=dict(title='Torres que dan vértigo',max=100,rows=[dict(l='Catedral',v=88,t='88 m',hl=True),dict(l='Acueducto',v=28,t='28 m'),dict(l='Torre Juan II',v=80,t='~80 m s. río',)],note='La torre de Juan II del Alcázar, medida desde el valle del Eresma. Valores aproximados.')),
 dict(id='juderia',n='9',short='Judería',name='Judería y Puerta de San Andrés',zone='Judería',time='17:00',stay=20,lat=40.94830,lon=-4.12640,gq='Puerta de San Andrés, Segovia',
  hook='El rabino que se bautizó con los Reyes Católicos de padrinos.',audio='audio/09.mp3',dur=58,
  images=[img('sanandres-1865','La Puerta de San Andrés en un grabado de 1865',year='1865'),img('murallas-juderia','La muralla que cerraba la judería por el sur'),img('juderia-calle','Placa de la calle de la Judería Vieja'),img('cementerio-judio','El Pinarillo, el antiguo cementerio judío, al otro lado del valle')],
  look='Desde el mirador de la Puerta de San Andrés, al otro lado del valle: El Pinarillo, el antiguo cementerio judío.',
  facts=[dict(tag='SALSEO',title='Padrinos reales',text='Abraham Seneor, rabino mayor de Castilla y financiero de Isabel, se bautizó en 1492 con los Reyes Católicos como padrinos.'),
         dict(tag='DATO',title='Nuevo nombre',text='Pasó a llamarse Fernán Pérez Coronel y conservó su posición en la corte.'),
         dict(tag='TIP',title='Domingo',text='El Centro Didáctico de la Judería cierra el domingo por la tarde: ved la fachada y bajad al mirador.')],
  timeline=[dict(y='1412',e='Se obliga a los judíos a vivir en la judería'),dict(y='1492',e='Decreto de expulsión'),dict(y='1492',e='Seneor se bautiza')]),
 dict(id='alcazar',n='10',short='Alcázar',name='Alcázar de Segovia',zone='Zona alta',time='17:40',stay=65,lat=40.95250,lon=-4.13210,gq='Alcázar de Segovia',alert='Hasta 20:00 · Última entrada 19:30',
  hook='El castillo-barco que media internet relaciona con Disney.',audio='audio/10.mp3',dur=69,
  images=[img('alcazar-otono','El Alcázar sobre el valle en otoño'),img('alcazar-2017','La proa del Alcázar al atardecer'),img('alcazar-1900','Fotocromo de hacia 1890-1900',year='c. 1900')],
  look='En la Sala del Cordón, el cordón franciscano que rodea el techo. Y la torre de Juan II: 152 escalones.',
  facts=[dict(tag='MITO',title='¿Inspiró a Disney?',text='No hay ningún documento que lo pruebe. El castillo de Disney se parece más a Neuschwanstein, en Baviera.',legend='Mito muy extendido'),
         dict(tag='FECHA',title='Incendio de 1862',text='El fuego destruyó tejados e interiores. Las agujas de pizarra son una reconstrucción de finales del siglo XIX.'),
         dict(tag='LEYENDA',title='Alfonso X y el rayo',text='El rey dijo que, de haber estado en la Creación, habría dado consejos a Dios. Cayó un rayo y se puso un cordón de penitencia.',legend='Leyenda'),
         dict(tag='SALSEO',title='Boda con la sobrina',text='En 1570 Felipe II se casó aquí con su cuarta esposa, Ana de Austria, que era su sobrina.'),
         dict(tag='DATO',title='Escuela de cadetes',text='Desde 1764 fue sede del Real Colegio de Artillería.')],
  numbers=[dict(v='152',l='escalones de la torre de Juan II'),dict(v='1862',l='año del gran incendio'),dict(v='~10',u='€',l='entrada completa')],
  ba=dict(before='img/alcazar-despues.webp',after='img/alcazar-otono.webp',by='Tras 1862',ay='Hoy',cap='Grabado del Alcázar tras el incendio de 1862, sin sus tejados, y el Alcázar hoy con las agujas reconstruidas.'),
  timeline=[dict(y='s. XII',e='Primer alcázar documentado'),dict(y='1474',e='Isabel sale de aquí a proclamarse reina'),dict(y='1570',e='Boda de Felipe II y Ana de Austria'),dict(y='1764',e='Real Colegio de Artillería'),dict(y='1862',e='Incendio'),dict(y='fin s. XIX',e='Reconstrucción de las cubiertas')]),
 dict(id='vuelta',n='B',short='Vuelta',name='Bajada al Acueducto y bus 11',kind='bus',zone='Vuelta',time='19:15',stay=0,lat=40.94720,lon=-4.11620,gq='Avenida del Padre Claret, Segovia',alert='Salid del Alcázar 18:50',
  hook='Veinte minutos cuesta abajo por la calle Real y autobús 11 a Guiomar.',audio='audio/11.mp3',dur=55,
  images=[img('acueducto-noche','El acueducto iluminado al anochecer')],
  info=[dict(t='Autobús línea 11 · Acueducto → Guiomar',badge='19:15-19:30',bc='ok',p='Sale de la cabecera en la avenida Padre Claret, al pie del acueducto. Unos 15-20 min. Unos 2 €, se puede pagar con tarjeta. Si va lleno, hay otro hacia las 19:40, pero va justo.'),
        dict(t='Plan B: taxi',p='Paradas en la Plaza Mayor y en el Azoguejo. Unos 11-12 € en domingo hasta Guiomar, 10-12 min. En el puente puede haber cola: mejor pedirlo hacia las 19:15.'),
        dict(t='No hay bus desde la zona alta',p='Ninguna línea va directa de la Plaza Mayor o el Alcázar a la estación. Lo más rápido es bajar andando (20-25 min) o taxi.')],
  look='El acueducto con la última luz: el sol se pone a las 19:43.'),
]
meta=dict(arrive='12:30',train='20:15',returnBus='19:15',walkDown=25)
planInfo=[dict(t='Ida: bus 11 desde Guiomar',badge='12:35-12:45',bc='ok',p='Sale de las dársenas delante de la estación y espera a los trenes. 15 min hasta el Acueducto. Unos 2 €, tarjeta o efectivo. En el puente se llena: salid rápido del andén.'),
 dict(t='Horarios del domingo',ul=['Corpus Christi: hasta 14:15 (1 €)','Casa de Machado: hasta 14:30, última entrada 14:15','Catedral: 13:30-18:30 (unos 4 €)','Alcázar: 10:00-20:00, última entrada 19:30 (unos 10 € con torre)','Centro de la Judería: cerrado por la tarde']),
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
legs=[]
for a,b in zip(stops,stops[1:]):
    na,nb=near(a['lon'],a['lat']),near(b['lon'],b['lat'])
    try:
        p=nx.shortest_path(G,na,nb,weight='w'); m=sum(G[u][v]['d'] for u,v in zip(p,p[1:]))
        coords=[[a['lon'],a['lat']]]+[[round(x,6),round(y,6)] for x,y in p]+[[b['lon'],b['lat']]]
    except Exception as e:
        coords=[[a['lon'],a['lat']],[b['lon'],b['lat']]]; m=hav(coords[0],coords[1])*1.3
    mins=max(2,round(m/65))
    legs.append(dict(coords=coords,m=int(round(m/10)*10),min=mins,mode='walk'))
    print(a['id'],'->',b['id'],int(m),'m',mins,'min')
legs[-1]['note']='casi todo cuesta abajo'
tour=dict(stops=stops,legs=legs,meta=meta,planInfo=planInfo,credits=credits)
t=open(SP+'template.html').read()
css=open(SP+'map/package/dist/maplibre-gl.css').read()
WEB='https://raw.githack.com/homerojimenez/App-visitas/HEAD/index.html'
t=t.replace('/*__MLCSS__*/',css).replace('/*__DATA__*/null',json.dumps(tour,ensure_ascii=False)).replace('/*__WEBURL__*/',WEB)
open(OUT+'artifact.html','w').write(t)
head='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1a6cf0"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Segovia"><meta name="apple-mobile-web-app-status-bar-style" content="default"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open(OUT+'index.html','w').write(head+t.replace('<meta charset="utf-8">\n','',1)+'</body></html>')
os.makedirs(OUT+'fonts/NotoReg',exist_ok=True); shutil.copy(SP+'map/glyph0.pbf',OUT+'fonts/NotoReg/0-255.ttf')
shutil.copy(SP+'map/map.json',OUT+'map.json')
os.makedirs(OUT+'img',exist_ok=True); os.makedirs(OUT+'audio',exist_ok=True)
for f in os.listdir(SP+'img'): shutil.copy(SP+'img/'+f,OUT+'img/'+f)
for f in os.listdir(SP+'audio'):
    shutil.copy(SP+'audio/'+f,OUT+'audio/'+('00.mp3' if f.startswith('00') else f))
print('ok', os.path.getsize(OUT+'index.html'))
