import numpy as np 
from PIL import Image
import random
import ui
import copy
from scene import *
import time
import matplotlib.pyplot as plt
from matplotlib import legend
from datetime import datetime
import os
import pickle

A = Action
WIDTH, HEIGHT = get_screen_size()

size_bot = 64
N_bot = 64
size_field = (50, 30)

COLOR = {'h':(0,190,0), '.':(0,0,0), 'w':(125,125,125), 'p':(190,0,0), 'b':(0,0,190)}

class bot():
	def __init__(self):
		self.code = 64*np.random.random((size_bot))
		self.code = np.floor(self.code)
		self.health = 90
		self.command = 0
		self.rot = 0
		self.generation = 0
		self.mutation = 0
		
	def execute_code(self):
		global size_bot
		self.health = self.health - 1
		turns = 0
		watches = 0
		skips = 0
		while True:
			if self.command>63:
				self.command -= 64
				assert 0<=self.command<=63
			command = self.code[self.command]
			if command<8:
				self.command += self.watch(command%8)
				self.move(command)
				break
			elif command<16:
				self.command += self.watch(command%8)
				self.catch(command%8)
				break
			elif command<24:
				self.command += self.watch(command%8)
				watches += 1
				if watches>10: break
			elif command<32:
				self.turn(command%8)
				self.command += 1
				turns += 1
				if turns>10: break
			else:
				self.command += command
				skips += 1
				if skips>30: break
				
	def get_direction(self, num):
		pos = self.pos
		num += self.rot
		if num>7: num = num%8
		assert 0<=num<=7
		if num==0:
			return (pos[0]-1, pos[1]+1)
		elif num==1:
			return (pos[0], pos[1]+1)
		elif num==2:
			return (pos[0]+1, pos[1]+1)
		elif num==3:
			return (pos[0]+1, pos[1])
		elif num==4:
			return (pos[0]+1, pos[1]-1)
		elif num==5:
			return (pos[0], pos[1]-1)
		elif num==6:
			return (pos[0]-1, pos[1]-1)
		elif num==7:
			return (pos[0]-1, pos[1])
	
	def move(self, num):
		init_pos = (self.pos[0], self.pos[1])
		self.pos = self.get_direction(num)	
		
		if check_field(self.pos)=='h':
			self.health += 10
			if self.health>90:
				self.set_health()
		elif check_field(self.pos)=='p':
			self.health = 0
		elif check_field(self.pos)=='w' or check_field(self.pos)=='b':
			self.pos = (init_pos[0], init_pos[1])
			
		set_field(init_pos, '.')
		set_field(self.pos, 'b')
			
	def catch(self, num):
		pos = self.get_direction(num)	
		if check_field(pos)=='h':
			self.health += 10
			if self.health>90:
				self.set_health()
			set_field(pos, '.')
		elif check_field(pos)=='p':
			set_field(pos, 'h')
		
	def watch(self, num):
		pos = self.get_direction(num)
		if check_field(pos)=='p':
			return 1
		elif check_field(pos)=='w':
			return 2
		elif check_field(pos)=='b':
			return 3
		elif check_field(pos)=='h':
			return 4
		else:
			return 5
		
	def turn(self, num):
		self.rot += num
		if self.rot>7: self.rot = self.rot%8
		
	def set_position(self, pos):
		self.pos = pos
		
	def mutate(self):
		i = random.randint(0,63)
		self.code[i] = random.randint(0,63)
		self.generation = 0
		self.mutation += 1
		
	def set_health(self):
		self.health = 90

def generate_field():
	global field 
	field = ('w'*(size_field[0]))+('w'+'.'*(size_field[0]-2)+'w')*(size_field[1]-2)+('w'*(size_field[0]))
	
	lenw = 0.4
	numw = 3
	
	for i in range(numw):
		for j in range(int(lenw*size_field[1])):
			x = (i+1)*int(size_field[0]/((numw+1)))
			y = int(size_field[1]*(1-(-1)**i)/2+j*(-1)**i)-1
			set_field((x,y), 'w')
	
	wf = 0.0
	hf = 0.1
	pf = 0.2
	
	x = 0
	while x<len(field):
		if field[x]!='.': 
			x += 1
			continue
		i = random.random()
		if i<wf:
			field = field[0:x] + 'w' + field[x+1:]
		elif i<hf:
			field = field[0:x] + 'h' + field[x+1:]
		elif i<pf:
			field = field[0:x] + 'p' + field[x+1:]
		x += 1
		
def check_field(pos):
	global field 
	return field[pos[0]+pos[1]*size_field[0]]
	
def set_field(pos, c):
	global field 
	x = pos[0]+pos[1]*size_field[0]
	field = field[0:x] + c + field[x+1:]
	
def mutate_field():
	Nh = field.count('h')
	Np = field.count('p')
	if Nh<(150): 
		insert_field('h', 150-Nh)
	if Np<150:
		insert_field('p', 150-Np)
		
def insert_field(str, num):
	global field
	i = 0
	n = 0
	MaxTrys = (size_field[0]*size_field[1])*10
	if num<1: return
	while (i<num) and (n<MaxTrys):
		n += 1
		x = random.randint(size_field[0], len(field)-size_field[0]-1)
		if (field[x]!='.') or (field[x-1]=='b') or (field[x+1]=='b') or (field[x+size_field[0]-1]=='b') or (field[x+size_field[0]+1]=='b') or (field[x+size_field[0]]=='b') or (field[x-size_field[0]+1]=='b') or (field[x-size_field[0]-1]=='b') or (field[x-size_field[0]]=='b'): continue
		field = field[:x]+str+field[x+1:]
		i += 1

def create_bots():
	global bots
	global copy_bots
	copy_bots = []
	bots = [bot() for _ in range(size_bot)]
	set_bots()
	
def set_bots():
	global bots
	global field
	for b in bots:
		while True:
			x = random.randint(0, len(field)-1)
			if field[x]!='.': 
				continue
			field = field[0:x] + 'b' + field[x+1:]
			b.set_position((x%size_field[0], x//size_field[0]))
			break

def execute_bots():
	global bots
	global iteration
	a = []
	for b in bots:
		b.execute_code()
		if b.health<=0:
			a.append(b)
			set_field(b.pos, '.')
			if (len(bots)-len(a))==8:
				if not len(copy_bots):
					save_bots(a)
	bots = [x for x in bots if x not in a]
	
def mutate_bots():
	global bots
	global copy_bots
	bots = copy_bots
	copy_bots = []
	a = []
	aa = []
	assert len(bots)==8
	for _ in range(4):
		a = a + [copy.deepcopy(x) for x in bots]
	for _ in range(3):
		aa = aa + [copy.deepcopy(x) for x in bots]
	for b in bots:
		b.mutate()
	for b in aa:
		b.mutate()
	bots = bots + a + aa
	set_bots()
	for b in bots:
		b.set_health()
		
def save_bots(a):
	global copy_bots, copy_bots_stat
	copy_bots = [copy.deepcopy(x) for x in bots if x not in a]
	copy_bots_stat = [copy.deepcopy(x) for x in bots if x not in a]
	for x in copy_bots:
		x.generation += 1
		x.command = 0

class GenAlg(Scene):
	def setup(self):
		generate_field()
		create_bots()
		self.iteration = 0
		self.generation = 0
		self.need_field = True
		self.isScene = True
		self.paused_state = False
		self.time = 0
		self.prev_time = time.clock()
		
		#Nodes
		self.background_color = (.0, .0, .0)
		self.Nrecords = 5
		self.NlastIters = 9
		self.root_node = Node(parent=self)
		self.time_label = LabelNode('Time: 00:00:00', font=('Helvetica', 30), color=(.49, .92, .86), position=(10, HEIGHT-40), parent=self.root_node, anchor_point=(0, 0.5))
		self.generation_label = LabelNode('Generation: 0', font=('Helvetica', 30), color=(.86, .47, .88), position=(10, HEIGHT-80), parent=self.root_node, anchor_point=(0, 0.5))
		self.iteration_label = LabelNode('Iteration: 0', font=('Helvetica', 30), color=(.91, .68, .43), position=(10, HEIGHT-120), parent=self.root_node, anchor_point=(0, 0.5))
		self.lastiteration_label = LabelNode('Last iteration: NaN', font=('Helvetica', 30), color=(.86, .34, .15), position=(10, HEIGHT-160), parent=self.root_node, anchor_point=(0, 0.5))
		self.record_label = LabelNode('Records:', font=('Helvetica', 30), color=(.43, 1, .83), position=(WIDTH-300, HEIGHT-40), parent=self.root_node, anchor_point=(0, 0.5))
		self.last_label = LabelNode('Last Iterations:', font=('Helvetica', 30), color=(1, .30, .15), position=(WIDTH-300, HEIGHT-(3+self.Nrecords)*40), parent=self.root_node, anchor_point=(0, 0.5))
		self.top_bot = LabelNode('NaN', font=('Courier', 20), color=(.9, .97, .74), position=(WIDTH-300, HEIGHT-(4+self.Nrecords+self.NlastIters)*40), parent=self.root_node, anchor_point=(0, 1.0))
				
		self.recordtable = [([0, 0], LabelNode('0 0', font=('Helvetica', 30), color=(.43, i/(self.Nrecords+1), .83), position=(WIDTH-300, HEIGHT-(i+2)*40), parent=self.root_node, anchor_point=(0, 0.5))) for i in range(self.Nrecords)]
		self.lasttable = [([-1, 0], LabelNode('0 0', font=('Helvetica', 30), color=(i/(self.NlastIters+1), .30, .15), position=(WIDTH-300, HEIGHT-(i+4+self.Nrecords)*40), parent=self.root_node, anchor_point=(0, 0.5))) for i in range(self.NlastIters)]
		self.treetable = [(LabelNode('H: NaN', font=('Helvetica', 25), color=(.12, i/9, .12), position=(280+(i-2)*90, HEIGHT-40), parent=self.root_node, anchor_point=(0, 0.5)), LabelNode('G: NaN', font=('Helvetica', 25), color=(i/9, .12, i/9), position=(280+(i-2)*90, HEIGHT-120), parent=self.root_node, anchor_point=(0, 0.5)), LabelNode('M: NaN', font=('Helvetica', 25), color=(.12, i/9, i/9), position=(280+(i-2)*90, HEIGHT-200), parent=self.root_node, anchor_point=(0, 0.5))) for i in range(2, 10)]
		
		
	def update(self):
		self.dt = time.clock() - self.prev_time
		if self.paused_state:
			return
		self.prev_time = time.clock()
		self.iteration += 1
		mutate_field()
		execute_bots()
		if self.need_field:
			self.print_field()
		self.time = self.time + self.dt
		self.time_label.text = 'Time: %02d:%02d:%02d' % (self.time//3600, self.time//60-self.time//3600*60, self.time%60)
		self.generation_label.text = 'Generation: %d' % (self.generation)
		self.iteration_label.text = 'Iteration: %d' % (self.iteration)
		if len(bots)==0:
			self.update_tree()
			generate_field()
			mutate_bots()
			if self.isScene==False:
				pass
				'''
				print('gen:', self.generation)
				print('it:', self.iteration)
				print()
				'''
			self.lastiteration_label.text = 'Last iteration: %d' % (self.iteration)
			self.update_records()
			self.generation += 1
			self.iteration = 0
			
	def print_field(self):
		im = [COLOR[i] for i in field]
		img = Image.new('RGB', (size_field[0], size_field[1]))
		img.putdata(im)
		img = img.resize((int(WIDTH*0.75), int(WIDTH*0.75*size_field[1]/size_field[0])))
		img.save('field.png')
		img = ui.Image.named('field.png')
		try:
			if self.img:
				self.img.remove_from_parent()
		except Exception:
			pass 
		self.img = SpriteNode(Texture(img), position=(WIDTH/2*0.75, WIDTH*0.75*size_field[1]/size_field[0]/2))
		self.root_node.add_child(self.img)
		
	def update_records(self):
		if self.iteration>self.recordtable[-1][0][1]:
			self.recordtable[-1][0][1] = self.iteration
			self.recordtable[-1][0][0] = self.generation
			self.recordtable[-1][1].text = '%d %d' % (self.generation, self.iteration)
			self.recordtable = sorted(self.recordtable, key=lambda x: x[0][1], reverse=True)
			for i,x in enumerate(self.recordtable):
				x[1].position = (WIDTH-300, HEIGHT-(i+2)*40)
				x[1].color = (.43, i/(self.Nrecords+1), .83)
				
		#update last table
		self.lasttable[-1][0][1] = self.iteration
		self.lasttable[-1][0][0] = self.generation
		self.lasttable[-1][1].text = '%d %d' % (self.generation, self.iteration)
		self.lasttable = sorted(self.lasttable, key=lambda x: x[0][0], reverse=True)
		for i,x in enumerate(self.lasttable):
			x[1].position = (WIDTH-300, HEIGHT-(i+4+self.Nrecords)*40)
			x[1].color = (i/(self.NlastIters+1), .30, .15)
		
	def update_tree(self):
		params = [(x.health, x.generation, x.mutation) for x in copy_bots]
		params = sorted(params, key=lambda x: x[0])
		for i,x in enumerate(self.treetable):
			x[0].text = 'H: %d' % params[i][0]
			x[1].text = 'G: %d' % params[i][1]
			x[2].text = 'M: %d' % params[i][2]
		
		max = 0	
		imax = -1
		for i,x in enumerate(copy_bots):
			if x.health>max:
				max = x.health 
				imax = i
				
		s = ''
		for i,x in enumerate(copy_bots[imax].code):
			if (i%8==0) and (i>0):
				s = s + '\n\n'
			s = s + '%02d ' % x
			
		self.top_bot.text = s	
		
		
	def touch_ended(self, touch):
		if (touch.location.x<WIDTH*0.75) and (touch.location.y<WIDTH*0.75*size_field[1]/size_field[0]):
			self.need_field = not self.need_field
		else:
			self.paused_state = not self.paused_state
			
def start_stat():
	global gen, iter, max_iter
	gen = []
	iter = []
	max_iter = []
			
def gather_stat(p):
	global gen, iter, max_iter
	if len(gen) == 0:
		gen.append(p.generation)
		iter.append(p.iteration)
	else:
		if gen[-1] == p.generation:
			iter[-1] = p.iteration
		else:
			gen.append(p.generation)
			iter.append(p.iteration)
			max_iter.append(max(iter))
			
def show_stat():
	global gen, iter, max_iter
	
	ax = plt.axes()
	plt.title('Life length vs time ({} Generations)'.format(str(len(gen) - 1)))
	plt.xlabel('Generations')
	plt.ylabel('Iterations')
	ax.grid(color='black', linestyle='-', linewidth=0.5)
	
	plt.plot(gen[:-1], iter[:-1], 'r-')
	plt.plot(gen[:-1], max_iter, 'm--')
	plt.plot(gen[:-1], [np.mean(iter[((i-5) if i >= 5 else 0):((i+5) if i < (len(iter[:-1])- 5) else -1)]) for i in range(len(iter[:-1]))], 'b--')
	plt.plot(gen[:-1], [np.mean(iter[:(i+1)]) for i in range(len(iter[:-1]))], 'g--')
	
	plt.legend(('Iterations', 'Maximum', 'Average', 'Mean of overall iterations'), loc='best')
	
	date = datetime.now()
	
	name = '{0}_gen_{1}|{2}|{3}_{4}:{5}.png'.format(str(len(gen) - 1), date.day, date.month, date.year, date.hour, date.minute)
	
	plt.savefig(os.path.join(curr_name, name))
	
	params = [(x.health, x.generation, x.mutation) for x in copy_bots_stat]
	params = sorted(params, key=lambda x: x[0])
	
	max = 0	
	for i,x in enumerate(copy_bots_stat):
		if x.health>max:
			max = x.health 
			imax = i
			
	s = 'Code:\n'
	for i,x in enumerate(copy_bots_stat[imax].code):
		if (i%8==0) and (i>0):
			s = s + '\n\n'
		s = s + '%02d ' % x
		
	s += '\n\n\nMutation:\n' + str(copy_bots_stat[imax].mutation)
			
	with open(os.path.join(curr_name, name[:-3] + '.txt'), 'w') as f:
		f.write(s)
	
def ran():
	global curr_name
	while True:
		date = datetime.now()
		curr_name = '{0}|{1}|{2}_{3}:{4}'.format(date.day, date.month, date.year, date.hour, date.minute)
		os.mkdir(curr_name)
		
		a = GenAlg()
		a.setup()
		a.need_field = False
		a.isScene = False
		start_stat()
		while a.generation < 1000:
			a.update()
			gather_stat(a)
			if a.generation % 10 == 0 and a.iteration == 0:
				show_stat()

if __name__ == '__main__':
	#run(GenAlg(), frame_interval=0.1)
	ran()
