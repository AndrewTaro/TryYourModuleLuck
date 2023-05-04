import random, json

#Order is IMPORTANT
GUN_COMPONENTS = ['artillery', 'torpedoes', 'atba', 'airDefense', 'depthCharges', 'chargeLasers', 'impulseLasers', 'axisLaser', 'waves', 'pinger']
OTHER_COMPONENTS = ['airArmament', 'engine']
HULL_COMPONENTS = ['steering_gear_hitlocation', 'simple_hitlocation', 'citadel_hitlocation', 'casemate_hitlocation', 'supersctructure_hitlocation', 'powdermagazine_hitlocation', 'hull_hitlocation']

COMPONENTS = GUN_COMPONENTS + OTHER_COMPONENTS

class HitLocation(object):
    def __init__(self, max_hp, rnd_part_hp):
        self.max_hp = max_hp
        self.rnd_part_hp = rnd_part_hp
        self.hp_coeff = 1.0

    def randomize_health(self, rand):
        min = 1.0 - self.rnd_part_hp
        max = 1.0 + self.rnd_part_hp
        self.hp_coeff = min + (max - min) * rand
        self.max_hp *= self.hp_coeff

    def __repr__(self):
        return 'max_hp: {}, hp_coeff: {}'.format(self.max_hp, self.hp_coeff)
        

def try_luck(vehicle_id, hit_locations):
    #save state
    _state = random.getstate()

    random.seed(vehicle_id)
    for hit_loc in hit_locations.values():
        hit_loc.randomize_health(random.random())

    #resore state
    random.setstate(_state)

    return hit_locations

def is_hitlocation(name, component):
    if isinstance(component, dict) and component.get('maxHP', None):
        return True
    if name.startswith('HP_'):
        for key in component:
            if key.startswith('HitLocation'):
                return True
    return False

def get_hitlocation(name, component):
    #hull hitlocations
    if isinstance(component, dict) and component.get('maxHP', None):
        name = '{}'.format(name)
        return (name, component)
    #other hitlocations
    if name.startswith('HP_'):
        for key in component:
            if key.startswith('HitLocation'):
                name = '{}.{}'.format(name, key)
                return (name, component[key])
    return None

def get_components(ship):
    hulls = [comp for comp_name, comp in ship['ShipUpgradeInfo'].iteritems() if comp_name[2:4] == 'UH']
    engines = [comp for comp_name, comp in ship['ShipUpgradeInfo'].iteritems() if comp_name[2:4] == 'UE']
    hulls[-1]['components']['engine'] = engines[-1]['components']['engine']
    return hulls[-1]['components']


def get_component(components, hl_type):
    for comp_name, comp in components.iteritems():
        if not isinstance(comp, dict) or 'hlType' not in comp:
        #if not hasattr(comp, 'hlType'):
            continue
        if comp['hlType'] != hl_type:
            continue
        yield (comp_name, comp)

def get_hitlocations(ship):
    hit_locations = {}
    components = get_components(ship)

    for _name in COMPONENTS:
        comps = components.get(_name)
        if comps is None or len(comps) == 0:
            continue
        comp_name = comps[-1]

        #print(comp_name)

        for module_name, module in ship[comp_name].iteritems():
            hit_loc = get_hitlocation(module_name, module)
            if hit_loc is None:
                continue

            name, hl = hit_loc

            hit_locations[name] = HitLocation(hl['maxHP'], hl['rndPartHP'])

    hull = components['hull'][-1]
    for _name in HULL_COMPONENTS:
        for comp_name, comp in get_component(ship[hull], _name):
            hit_locations[comp_name] = HitLocation(comp['maxHP'], comp['rndPartHP'])

    return hit_locations


SHIP_NAME = 'PFSD110_Kleber'
ENTITY_ID = 811267

def main():
    filename = 'Ship\\{}.json'.format(SHIP_NAME)
    with open(filename, 'r') as f:
        ship = json.load(f)
    #with open('all_gameparams.json', 'r') as f:
    #    gp = json.load(f)
    #gp = gp[0]

    #ship = gp.get(SHIP_NAME)

    hit_locations = get_hitlocations(ship)

    try_luck(ENTITY_ID, hit_locations)

    for hl_name, hl in hit_locations.iteritems():
        print(hl_name, hl)


if __name__ == '__main__':
    main()