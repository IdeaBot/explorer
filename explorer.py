from addons.UIdea.libs import ui as ui_class
import re
import random
import json
from addons.explorer.libs import dungeon, people

DIALOG_JSON = 'addons/explorer/resources/dialogs.json'
with open(DIALOG_JSON, 'r') as f:
    DIALOGS = json.load(f)
DUNGEON_DIALOGS = DIALOGS['ondungeon']

INVENTORY_SLOTS = ["📗", "📙", "📘"]

class UI(ui_class.UI):
    def shouldCreate(msg):
        return collect_args(msg) is not None

    def onCreate(self, msg):
        if re.search(r'\s-v\b', msg.content) is None:
            self.is_verbose = False
        else:
            self.is_verbose = True
        self.dungeon_num = 0
        self.player = people.Player()
        self.tenretni = people.Internet()
        self.cixot = people.Toxic()
        self._next_dungeon()
        # build fields
        self.embed.add_field(name='Inventory', value='Work In Progress')  # field 0 for inventory
        self.embed.add_field(name='Level %s' % self.player.level, value=self._make_stats_str(self.player)) # field 1 for stats
        self.embed.add_field(name='Dialog', value='.')
        if self.is_verbose:
            self.embed.add_field(name='Debug', value='.') # field 3 for debug
        self._update_embed()

    def attackOne(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.attack(1, target=self.player.get_target())
        self._do_turn()

    def attackTwo(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.attack(2, target=self.player.get_target())
        self._do_turn()

    def attackThree(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.attack(3, target=self.player.get_target())
        self._do_turn()

    def moveLeft(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.move_left()
        self._do_turn()

    def moveRight(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.move_right()
        self._do_turn()

    def moveUp(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.move_up()
        self._do_turn()

    def moveDown(self, reaction, user):
        if self.player.health == 0:
            return
        self.player.move_down()
        self._do_turn()

    def _update_embed(self):
        self.embed.description = '```' + self.current_dungeon.draw_board() + '```'
        # Populate inventory
        self.embed.set_field_at(0, name='Inventory', value=self._make_inventory_str(self.player))
        # Populate inventory
        self.embed.set_field_at(1, name='Level %s' % self.player.level, value=self._make_stats_str(self.player))
        self.embed.set_field_at(2, name='Dialog', value=self._make_dialog())
        if self.is_verbose:
            # Populate debug
            self.embed.set_field_at(3, name='Debug', value='.')
        self.update()

    def _make_inventory_str(self, person):
        if len(person.inventory) > 0:
            inv_str = ''
            for n in range(3):
                if len(person.inventory) > n:
                    i = person.inventory[n]
                    inv_str += INVENTORY_SLOTS[n]
                    inv_str += + ' ' + i['name']
                    inv_str += ' **(+' + i['damage'] + ')**'
                    inv_str += '\n'
            return inv_str
        else:
            return INVENTORY_SLOTS[0] + ' nothing **(+0)**'


    def _make_stats_str(self, person):
        stats_str = ''
        stats_str += 'HP: ' + str(person.health) + '/' + str(person.basehealth*person.level) + '\n'
        stats_str += 'DMG: ' + str(person.damage) + '\n'
        stats_str += 'SPD: ' + str(person.speed) + '\n'
        return stats_str

    def _make_dialog(self):
        if self.player.health == 0:
            return '**You died :\'(**'
        if str(self.dungeon_num) in DUNGEON_DIALOGS and DUNGEON_DIALOGS[str(self.dungeon_num)] != '':
            return DUNGEON_DIALOGS[str(self.dungeon_num)]
        else:
            return self.embed.fields[2].value

    def _next_dungeon(self):
        self.dungeon_num += 1
        self.current_dungeon = dungeon.Dungeon(level=self.dungeon_num)
        # spawn enemies
        for i in range(random.randint(1, (self.dungeon_num//2)+1)):
            people.Outside(self.current_dungeon)
        if random.choice([True, False]):
            people.Polite(self.current_dungeon)
        # teleport friendlies
        self.player.teleport(self.current_dungeon)
        self.tenretni.teleport(self.current_dungeon)
        self.cixot.teleport(self.current_dungeon)

    def _do_turn(self):
        self.current_dungeon.do_turn()
        self._update_embed()
        if self.current_dungeon.find_person(self.player.name) is None:
            # you dead son
            return
        if self.current_dungeon.find_person(self.player.name) in self.current_dungeon.portals:
            self._next_dungeon()
            self._update_embed()


def collect_args(msg):
    return re.search(r'\bexplore\b', msg.content, re.I)
