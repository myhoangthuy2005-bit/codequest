"""Campus Shop catalogue and backwards-compatible per-profile cosmetic inventory."""
CATEGORIES = {
    'background': 'Campus backgrounds',
    'title': 'Player titles',
    'effect': 'Victory effects',
    'ornament': 'Card ornaments',
}
CATALOGUE = {
    'campus': dict(category='background', name='Academy courtyard', price=0, description='The original warm campus evening.', image=''),
    'jacaranda': dict(category='background', name='Jacaranda afternoon', price=80, description='Purple blossoms above golden sandstone arches.', image='jacaranda.webp'),
    'library': dict(category='background', name='Fisher after hours', price=100, description='Warm reading lamps and a peaceful midnight study room.', image='library.webp'),
    'rainy': dict(category='background', name='Rainy Quadrangle', price=120, description='Blue-hour rain, golden windows and reflected light.', image='rainy.webp'),
    'student': dict(category='title', name='Student', price=0, description='Every codebreaker starts somewhere.'),
    'midnight-coder': dict(category='title', name='Midnight Coder', price=25, description='For the late-night problem solvers.'),
    'python-scholar': dict(category='title', name='Python Scholar', price=45, description='Wear your curiosity with pride.'),
    'campus-codebreaker': dict(category='title', name='Campus Codebreaker', price=60, description='A title worthy of the academy.'),
    'none': dict(category='effect', name='Quiet celebration', price=0, description='A calm, distraction-free finish.'),
    'petals': dict(category='effect', name='Jacaranda shower', price=40, description='A brief cascade of purple petals after a scored win.'),
    'sparkles': dict(category='effect', name='Golden moment', price=60, description='A shower of soft golden stars after a scored win.'),
    'code-rain': dict(category='effect', name='Code celebration', price=70, description='Floating braces and Python symbols celebrate your answer.'),
    'classic': dict(category='ornament', name='Academy gold', price=0, description='The original restrained golden flourishes.'),
    'gothic': dict(category='ornament', name='Gothic arches', price=35, description='Sandstone-inspired arches frame each card.'),
    'botanical': dict(category='ornament', name='Jacaranda vines', price=45, description='Botanical borders with tiny purple blossoms.'),
    'illuminated': dict(category='ornament', name='Illuminated gold', price=70, description='Layered golden edging and ornamental manuscript corners.'),
}
DEFAULT_EQUIPMENT = dict(background='campus', title='student', effect='none', ornament='classic')

def normalize_cosmetics(profile):
    """Upgrade old saves, preserving valid purchases and repairing invalid equipment."""
    value=profile.get('cosmetics')
    if not isinstance(value,dict):value={}
    owned=value.get('owned',[])
    if not isinstance(owned,list):owned=[]
    owned=list(dict.fromkeys(i for i in owned if isinstance(i,str) and i in CATALOGUE))
    for item in DEFAULT_EQUIPMENT.values():
        if item not in owned:owned.append(item)
    equipped=value.get('equipped',{})
    if not isinstance(equipped,dict):equipped={}
    safe={}
    for category,default in DEFAULT_EQUIPMENT.items():
        chosen=equipped.get(category)
        safe[category]=chosen if isinstance(chosen,str) and chosen in owned and CATALOGUE[chosen]['category']==category else default
    profile['cosmetics']=dict(owned=owned,equipped=safe)
    return profile['cosmetics']
