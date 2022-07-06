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
	
	def convert_to_2D(self, point, x, y, p, win):
		point_2D = func_3d_to_2d(self.get_vector4(), point, x, y, p, win)
		return Point(point_2D[0], point_2D[1])


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
	faces = np.array([
		[0, 1, 2, 3, 0], # пол
		[6, 10, 11, 7, 6], # стена 1
		[8, 4, 7, 11, 8], # стена 2
		[9, 5, 6, 10, 9], # стена 3
		[9, 5, 4, 8, 9], # стена 4
		[12, 4, 7, 12, -1], # крыша перед
		[17, 5, 6, 17, -1], # крыша зад
		[4, 5, 17, 12, 4], # крыша 1
		[7, 6, 17, 12, 7], # крыша 2
		[4, 5, 6, 7, 4] # потолок
		], dtype=int)
	
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
		
		self.lines.append([Point3D(-length / 2, 0, height1 + height2), Point3D(length / 2, 0, height1 + height2)])
	
	def weight_center(self):
		xc = 0
		yc = 0
		zc = 0
		
		for i in range(8):
			xc += self.lines[i][0].x
			yc += self.lines[i][0].y
			zc += self.lines[i][0].z
		xc += self.lines[12][0].x
		yc += self.lines[12][0].y
		zc += self.lines[12][0].z
		xc += self.lines[17][0].x
		yc += self.lines[17][0].y
		zc += self.lines[17][0].z
		
		return np.array([xc / 10, yc / 10, zc / 10])
	
	def body_matrix(self):
		matrix = np.zeros((4, 9))
		for i in range(9):
			matrix[0][i] = (self.lines[self.faces[i][2]][0].y - self.lines[self.faces[i][0]][0].y) * (self.lines[self.faces[i][1]][0].z - self.lines[self.faces[i][0]][0].z) - (self.lines[self.faces[i][1]][0].y - self.lines[self.faces[i][0]][0].y) * (self.lines[self.faces[i][2]][0].z - self.lines[self.faces[i][0]][0].z)
			matrix[1][i] = (self.lines[self.faces[i][1]][0].x - self.lines[self.faces[i][0]][0].x) * (self.lines[self.faces[i][2]][0].z - self.lines[self.faces[i][0]][0].z) - (self.lines[self.faces[i][2]][0].x - self.lines[self.faces[i][0]][0].x) * (self.lines[self.faces[i][1]][0].z - self.lines[self.faces[i][0]][0].z)
			matrix[2][i] = (self.lines[self.faces[i][2]][0].x - self.lines[self.faces[i][0]][0].x) * (self.lines[self.faces[i][1]][0].y - self.lines[self.faces[i][0]][0].y) - (self.lines[self.faces[i][1]][0].x - self.lines[self.faces[i][0]][0].x) * (self.lines[self.faces[i][2]][0].y - self.lines[self.faces[i][0]][0].y)
			matrix[3][i] = -(matrix[0][i] * self.lines[self.faces[i][0]][0].x + matrix[1][i] * self.lines[self.faces[i][0]][0].y + matrix[2][i] * self.lines[self.faces[i][0]][0].z)
		return matrix
	
	def visible_faces(self, point):
		matrix = self.body_matrix()
		weight_center = self.weight_center()
		result_numbers = np.array([])
		for i in range(9):
			if (matrix[0][i] * weight_center[0] + matrix[1][i] * weight_center[1] + matrix[2][i] * weight_center[2] + matrix[3][i] < 0):
				for j in range(4):
					matrix[j][i] *= -1
			if (matrix[0][i] * point.x + matrix[1][i] * point.y + matrix[2][i] * point.z < 0):
				result_numbers = np.append(result_numbers, i)
		return result_numbers
	
	def face_draw(self, i, point, x, y, p, win, color = 'blue'):
		j = 1
		points = []
		i = int(i)
		points.append(self.lines[self.faces[i][0]][0].convert_to_2D(point, x, y, p, win))
		while (self.faces[i][j] != self.faces[i][0]):
			points.append(self.lines[self.faces[i][j]][0].convert_to_2D(point, x, y, p, win))
			Line(points[j - 1], points[j]).draw(win)
			j += 1
		Line(points[j - 1], points[0]).draw(win)
		face = Polygon(points)
		face.setFill(color)
		face.draw(win)
	
	def draw_visible_faces(self, point, x, y, p, win, color = 'blue', color2 = 'red', color3 = 'gray'):
		faces_to_draw = self.visible_faces(point)
		for i in range(faces_to_draw.size):
			if (faces_to_draw[i] == 0):
				self.face_draw(faces_to_draw[i], point, x, y, p, win, color3)
			elif (faces_to_draw[i] < 5):
				self.face_draw(faces_to_draw[i], point, x, y, p, win, color)
			elif (faces_to_draw[i] < 10):
				self.face_draw(faces_to_draw[i], point, x, y, p, win, color2)
	
	def draw(self, point, x, y, p, win, color = 'black'):
		for i in range(17):
			line_draw(line_convert_p_arr(self.lines[i], point, x, y, p, win), win, color)
		line_draw(line_convert_p_arr(self.lines[8], point, x, y, p, win), win, 'red', 3)
		point_house = func_3d_to_2d(self.lines[10][0].get_vector4(), point, x, y, p, win)
		point_house_object = Circle(Point(point_house[0], point_house[1]), 3)
		point_house_object.setOutline('red')
		point_house_object.setFill('red')
		point_house_object.draw(win)
		
		gr_points = []
		gr_points.append(self.lines[8][0].convert_to_2D(point, x, y, p, win))
		gr_points.append(self.lines[8][1].convert_to_2D(point, x, y, p, win))
		gr_points.append(self.lines[11][1].convert_to_2D(point, x, y, p, win))
		gr_points.append(self.lines[11][0].convert_to_2D(point, x, y, p, win))
		
		gr = Polygon(gr_points)
		gr.setFill('blue')
		gr.draw(win)

def main():
	win = GraphWin("House (lab3)", 700, 600, autoflush=False)
	
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
	#house.draw(point, x, y, p, win)
	house.draw_visible_faces(point, x, y, p, win)
	
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
		
		#house.draw(point, x, y, p, win)
		house.draw_visible_faces(point, x, y, p, win)
		
		win.update()
		
		time.sleep(0.1)
	
	print("Done!")
		
	
	win.getMouse()
	clear(win)
	win.close()

if __name__ == '__main__':
	main()
