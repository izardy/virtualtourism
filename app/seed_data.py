"""Seed content for the MVP destination: Muzium Perang Penang. Positions are glTF metres from blender/out/hotspots.json."""

DESTINATION = dict(
    name="Muzium Perang Penang",
    location="Batu Maung, Penang, Malaysia",
    category="Museum / Historical Landmark",
    thumbnail="images/muzium_perang_thumb.jpg",
    hero_image="images/muzium_perang_hero.jpg",
    model_path="models/muzium_perang.glb",
    description="Muzium Perang Penang, the Penang War Museum, stands on Bukit Batu Maung at the south-east tip of Penang Island. It is a former British coastal fort: British Royal Engineers began building it in 1930 and completed it around 1939, on roughly eight hectares of hillside above the Strait of Malacca. Its guns, tunnels and barracks were built to defend the island from attack by sea.\n\nWhen Japanese forces invaded Malaya in December 1941, Penang fell quickly. The Japanese used the fort as a base and a place of detention, and local people still call the hill Bukit Hantu, Ghost Hill. The stories of ghosts are folklore. The suffering of the prisoners held here was real, and the site is treated as a memorial.\n\nAfter the war the fort was abandoned and overgrown for decades. Restoration began in the late 1990s, led by local businessman Johari Shafie, and the site opened as a museum in 2002. A memorial to the war dead was added in 2003. This 3D tour is an unofficial, provisional reconstruction based on the museum's public visitor map and licensed photographs, made for education and exploration.",
)

HOTSPOTS = [
    dict(
        title='Main Entrance', # provisional position: False
        description='Your tour starts at the ticketing building at the foot of Bukit Batu Maung. From here a path climbs through the old fort, past barracks, gun bays and tunnels. The site covers roughly eight hectares of hillside above the Strait of Malacca.\n\nFacts:\n- The fort was built by British Royal Engineers from 1930 and completed around 1939.\n- It opened to the public as a museum in 2002, after years of restoration.\n- Locals know the hill as Bukit Hantu, or Ghost Hill.',
        x_position=0.0, y_position=-4.81, z_position=-0.0,
        image_path='images/hotspots/main-entrance.jpg', audio_path='audio/main-entrance.mp3',
    ),
    dict(
        title='Japanese Tunnel', # provisional position: True
        description='Concrete tunnels link different parts of the fort, from ammunition stores to the communications area. After Japanese forces took the fort, it served as a base and a place of detention. Which tunnel carries the name Japanese Tunnel should be confirmed with the signs on site.\n\nFacts:\n- Tunnels on site are numbered, for example No. 8.\n- The museum advises visiting the deeper tunnels with a guide.\n- The air inside stays cool and damp, even at midday.',
        x_position=81.8, y_position=3.68, z_position=86.4,
        image_path='images/hotspots/japanese-tunnel.jpg', audio_path='audio/japanese-tunnel.mp3',
    ),
    dict(
        title='Command Centre', # provisional position: False
        description='The museum map marks an intelligence room and an underground communication centre near the middle of the fort. From rooms like these, officers coordinated the gun batteries. A sign on site explains that underground cable carried electricity for the large artillery operations of British troops in the Second World War.\n\nFacts:\n- The fort held cannons, anti-aircraft guns and pillboxes.\n- The British expected an attack from the sea, but the Japanese advanced overland.\n- Exact room layouts here are an estimate.',
        x_position=-84.8, y_position=-14.39, z_position=46.4,
        image_path=None, audio_path='audio/command-centre.mp3',
    ),
    dict(
        title='Observation Tower', # provisional position: False
        description='At the top of the main path, an observation post looks out over the sea lanes of the Strait of Malacca. Spotters here watched for ships, and reported to the guns. One visitor guide describes a three hundred and twenty degree view from this part of the fort.\n\nFacts:\n- The hill was chosen for its clear view of the sea.\n- The map marks this as the Observation Post, number 24.\n- The structure here is modelled from the museum map and photos, so details are approximate.',
        x_position=-39.2, y_position=1.86, z_position=104.8,
        image_path=None, audio_path='audio/observation-tower.mp3',
    ),
    dict(
        title='Prison Area', # provisional position: False
        description='After the Japanese took the fort, parts of it were used to hold prisoners. The museum marks a lock-up, a Japanese-era torture chamber, a mortuary and a guillotine. These were places of real suffering, so please move through them with respect. Stories of ghosts here are local folklore, not history.\n\nFacts:\n- Locals call the hill Bukit Hantu, Ghost Hill, because of the executions remembered here.\n- Cells have barred doors and bare concrete walls.\n- Please treat this area as a memorial.',
        x_position=-101.8, y_position=-15.23, z_position=58.6,
        image_path='images/hotspots/prison-area.jpg', audio_path='audio/prison-area.mp3',
    ),
    dict(
        title='Underground Bunker', # provisional position: True
        description='Thick concrete rooms, half buried under earth, protected soldiers and equipment from air and naval attack. The museum map shows an underground communication centre, an underground water tank and an armoury close together. Heavy doors and grates still guard the openings.\n\nFacts:\n- Signs on hatches read Merbahaya, Malay for Dangerous.\n- Earth over the roof helped absorb the force of bombs and shells.\n- The exact function of each bunker needs confirming with museum signs.',
        x_position=-50.2, y_position=-8.45, z_position=45.9,
        image_path='images/hotspots/underground-bunker.jpg', audio_path='audio/underground-bunker.mp3',
    ),
    dict(
        title='Memorial Zone', # provisional position: True
        description="A black granite plaque reads To Our Glorious Dead, and below it lists the conflicts that touched Malaysia: World War One, World War Two, the Siam Burma Death Railway, the Malayan Emergency, the Indonesian Confrontation and the Re-insurgency period. It ends with the words Lest We Forget.\n\nFacts:\n- The plaque lists 1914 to 1918, 1939 to 1945, 1942 to 1945, 1948 to 1960, 1963 to 1966 and 1968 to 1990.\n- The memorial was sponsored by the Penang War Veterans Association and finished in 2003.\n- The memorial's exact position in this model is an estimate.",
        x_position=10.0, y_position=-0.39, z_position=75.0,
        image_path='images/hotspots/memorial-zone.jpg', audio_path='audio/memorial-zone.mp3',
    ),
    dict(
        title='Weapons Display', # provisional position: False
        description="Circular concrete gun bays, each with a central pivot, once held the fort's coastal artillery. Anti-aircraft pits and pillboxes cover the hillside around them. A sign on site names this the Penang Fortress Battery.\n\nFacts:\n- The fort had cannons, anti-aircraft guns and pillboxes.\n- Each gun sat on a pivot at the centre of its concrete ring.\n- The cannon models here are stand-ins, not the original guns.",
        x_position=14.9, y_position=2.28, z_position=95.3,
        image_path='images/hotspots/weapons-display.jpg', audio_path='audio/weapons-display.mp3',
    ),
    dict(
        title='Lookout Point', # provisional position: True
        description="From the edge of the hill, the Strait of Malacca stretches out below. This is why the British chose Bukit Batu Maung: whoever held this ridge could see every ship approaching the island. Today the lookout is a quiet place to take in the view.\n\nFacts:\n- The coast lies a few hundred metres to the east.\n- Pillboxes along the shore covered the beaches below.\n- This viewpoint's position in the model is an estimate.",
        x_position=77.2, y_position=3.54, z_position=95.9,
        image_path='images/hotspots/lookout-point.jpg', audio_path='audio/lookout-point.mp3',
    ),
    dict(
        title='Escape Route', # provisional position: True
        description="A sign reads Escape route to top, with a note: seven metres crawl, nine metres climb, and a cheerful message, You can do it. A narrow concrete shaft with a steel ladder leads up through the hill. In this reconstruction the climb is shortened.\n\nFacts:\n- The real route is a 7 metre crawl followed by a 9 metre ladder climb.\n- The shaft is about as wide as a person's shoulders.\n- The location of this route in the model is an estimate.",
        x_position=44.86, y_position=0.3, z_position=88.85,
        image_path='images/hotspots/escape-route.jpg', audio_path='audio/escape-route.mp3',
    ),
]
