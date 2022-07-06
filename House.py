from graphics import *
import time
import math
import numpy as np

def sign(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

def clear(win):
	for item in win.items[:]:
		item.undraw()

class Point3D():
	x = 0
	y = 0
	z = 0
	
	def __init__(self, X = 0, Y = 0, Z = 0):
		self.x = X
		self.y = Y
		self.z = Z
		
	def set_coordinates(self, X, Y, Z):
		self.x = X
		self.y = Y
		self.z = Z
	
	def set_x(self, X):
		self.x = X
	
	def set_y(self, Y):
		self.y = Y
	
	def set_z(self, z):
		self.z = Z
	
	def get_vector(self):
		return np.array([self.x, self.y, self.z])
	
	def get_vector4(self):
		return np.array([self.x, self.y, self.z, 1])


def world_to_spectator(vector, point):
	T = np.eye(4)
	T[3][0] = -point.x
	T[3][1] = -point.y
	T[3][2] = -point.z
	return vector @ T

def cs_x_invert_y_up(vector):
	SR = np.zeros((4, 4))
	SR[0][0] = -1
	SR[1][2] = -1
	SR[2][1] = 1
	SR[3][3] = 1
	return vector @ SR

def cs_z_to_cs_start(vector, point):
	R1 = np.eye(4)
	R2 = np.eye(4)
	d = (point.x ** 2 + point.y ** 2) ** 0.5
	s = (point.x ** 2 + point.y ** 2 + point.z ** 2) ** 0.5
	if (d != 0):
		R1[0][0] = point.y / d
		R1[0][2] = point.x / d
		R1[2][0] = -point.x / d
		R1[2][2] = point.y / d
	if (s != 0):
		R2[1][1] = d / s
		R2[1][2] = -point.z / s
		R2[2][1] = point.z / s
		R2[2][2] = d / s
	return vector @ R1 @ R2

def paralell(vector):
	return np.array([vector[0], vector[1]])

def perspective(vector, point):
	s = (point.x ** 2 + point.y ** 2 + point.z ** 2) ** 0.5
	return np.array([vector[0] * s / vector[2], vector[1] * s / vector[2]])

def screen_cs(vector, x, y, p, win):
	return np.array([vector[0] * x / p + win.width / 2, win.height / 2 - vector[1] * y / p])

def func_3d_to_2d(vector, point, x, y, p, win):
	return screen_cs(paralell(cs_z_to_cs_start(cs_x_invert_y_up(world_to_spectator(vector, point)), point)), x, y, p, win)

def line_convert(point1, point2, point_view, x, y, p ,win):
	return np.array([func_3d_to_2d(point1.get_vector4(), point_view, x, y, p, win), func_3d_to_2d(point2.get_vector4(), point_view, x, y, p, win)])

def line_convert_p_arr(line, point_view, x, y, p ,win):
	return np.array([func_3d_to_2d(line[0].get_vector4(), point_view, x, y, p, win), func_3d_to_2d(line[1].get_vector4(), point_view, x, y, p, win)])

def line_draw(line, win, color = 'black', width = 1):
	line = Line(Point(line[0][0], line[0][1]), Point(line[1][0], line[1][1]))
	line.setOutline(color)
	line.setWidth(width)
	line.draw(win)

def dotted_line_draw(line, win, length = 20, color = 'black'):
	dx = line[1][0] - line[0][0]
	dy = line[1][1] - line[0][1]
	
	if (dx == 0 and dy == 0):
		return
	
	prev_x = line[0][0]
	prev_y = line[0][1]
	
	if (dx != 0):
		c = ((length ** 2) / ((dy / dx) ** 2 + 1)) ** 0.5
		a = dy / dx
		b = (line[0][1] * line[1][0] - line[1][1] * line[0][0]) / dx
	else:
		c = 0
		a = 0
		b = 0
	
	for i in range(round(math.sqrt((dx ** 2 + dy ** 2)) / (length * 2))):
		x1 = prev_x
		y1 = prev_y
		
		x2 = c * sign(dx) + x1
		y2 = a * x2 + b
		
		prev_x = c * sign(dx) + x2
		prev_y = a * prev_x + b
		
		if (dx == 0):
			x2 = x1
			y2 = y1 + length * sign(dy)
			prev_x = x1
			prev_y = y2 + length * sign(dy)
		if (dy == 0):
			y2 = y1
			x2 = x1 + length * sign(dx)
			prev_y = y1
			prev_x = x2 + length * sign(dx)
		
		line_temp = Line(Point(x1, y1), Point(x2, y2))
		line_temp.setOutline(color)
		line_temp.draw(win)

class House():
	lines = []
	
	def __init__(self, length = 0, width = 0, height1 = 0, height2 = 0):
		self.lines.append([Point3D(length / 2, width / 2, 0), Point3D(-length / 2, width / 2, 0)])
		self.lines.append([Point3D(-length / 2, width / 2, 0), Point3D(-length / 2, -width / 2, 0)])
		self.lines.append([Point3D(-length / 2, -width / 2, 0), Point3D(length / 2, -width / 2, 0)])
		self.lines.append([Point3D(length / 2, -width / 2, 0), Point3D(length / 2, width / 2, 0)])
		
		self.lines.append([Point3D(length / 2, width / 2, height1), Point3D(-length / 2, width / 2, height1)])
		self.lines.append([Point3D(-length / 2, width / 2, height1), Point3D(-length / 2, -width / 2, height1)])
		self.lines.append([Point3D(-length / 2, -width / 2, height1), Point3D(length / 2, -width / 2, height1)])
		self.lines.append([Point3D(length / 2, -width / 2, height1), Point3D(length / 2, width / 2, height1)])
		
		self.lines.append([Point3D(length / 2, width / 2, 0), Point3D(length / 2, width / 2, height1)])
		self.lines.append([Point3D(-length / 2, width / 2, 0), Point3D(-length / 2, width / 2, height1)])
		self.lines.append([Point3D(-length / 2, -width / 2, 0), Point3D(-length / 2, -width / 2, height1)])
		self.lines.append([Point3D(length / 2, -width / 2, 0), Point3D(length / 2, -width / 2, height1)])
		
		self.lines.append([Point3D(length / 2, 0, height1 + height2), Point3D(-length / 2, 0, height1 + height2)])
		
		self.lines.append([Point3D(length / 2, width / 2, height1), Point3D(length / 2, 0, height1 + height2)])
		self.lines.append([Point3D(length / 2, -width / 2, height1), Point3D(length / 2, 0, height1 + height2)])
		self.lines.append([Point3D(-length / 2, width / 2, height1), Point3D(-length / 2, 0, height1 + height2)])
		self.lines.append([Point3D(-length / 2, -width / 2, height1), Point3D(-length / 2, 0, height1 + height2)])
	
	def draw(self, point, x, y, p, win, color = 'black'):
		for i in range(17):
			line_draw(line_convert_p_arr(self.lines[i], point, x, y, p, win), win, color)
		line_draw(line_convert_p_arr(self.lines[8], point, x, y, p, win), win, 'red', 3)
		point_house = func_3d_to_2d(self.lines[10][0].get_vector4(), point, x, y, p, win)
		point_house_object = Circle(Point(point_house[0], point_house[1]), 3)
		point_house_object.setOutline('red')
		point_house_object.setFill('red')
		point_house_object.draw(win)

def main():
	win = GraphWin("House (lab2)", 700, 600, autoflush=False)
	
	point = Point3D(5, 0, 1)
	x = 350
	y = 300
	p = 10
	
	o = Point3D(0, 0, 0)
	ox = Point3D(100, 0, 0)
	oy = Point3D(0, 100, 0)
	oz = Point3D(0, 0, 100)
	
	line_x = line_convert(o, ox, point, x, y, p, win)
	dotted_line_draw(line_x, win, 20, 'gray')
	
	line_y = line_convert(o, oy, point, x, y, p, win)
	dotted_line_draw(line_y, win, 20, 'gray')
	
	line_z = line_convert(o, oz, point, x, y, p, win)
	dotted_line_draw(line_z, win, 20, 'gray')
	
	house = House(6, 4, 2, 1)
	house.draw(point, x, y, p, win)
	
	win.update()
	
	time.sleep(1)
	
	frames_coefficient = 3
	angle = math.pi / (180 * frames_coefficient)
	
	for i in range((30 * frames_coefficient)):
		point.set_coordinates(point.x * math.cos(angle) - point.y * math.sin(angle), point.x * math.sin(angle) + point.y * math.cos(angle), point.z)
		
		clear(win)
		line_x = line_convert(o, ox, point, x, y, p, win)
		dotted_line_draw(line_x, win, 20, 'gray')
		line_y = line_convert(o, oy, point, x, y, p, win)
		dotted_line_draw(line_y, win, 20, 'gray')
		line_z = line_convert(o, oz, point, x, y, p, win)
		dotted_line_draw(line_z, win, 20, 'gray')
		
		house.draw(point, x, y, p, win)
		
		win.update()
		
		time.sleep(0.1)
	
	print("Done!")
		
	
	win.getMouse()
	clear(win)
	win.close()

if __name__ == '__main__':
	main()
