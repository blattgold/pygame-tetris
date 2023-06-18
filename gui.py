from enum import Enum
import pygame

class Element:
    x = 0
    y = 0
    actual_x = 0
    actual_y = 0
    w = 1
    h = 1
    parent = False # False = top level, no parent
    center_origin = False

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.w = 1
        self.h = 1

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_actual_x(self):
        return self.actual_x

    def get_actual_y(self):
        return self.actual_y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_h(self):
        return self.h

    def get_w(self):
        return self.w

    def update(self):
        pass

    def draw(self, x_off=0, y_off=0):
        pass

    def set_parent(self, element):
        self.parent = element
        self.update()

    def get_centered(self):
        return self.center_origin

class Text(Element):
    content = False
    font = False

    def __init__(self, content, font, x=0, y=0):
        super().__init__(x, y)
        self.content = content
        self.font = font
        self.w = int(self.font.render(self.content, True, (0,0,0)).get_width())
        self.h = int(self.font.render(self.content, True, (0,0,0)).get_height())

    def draw(self, screen, x_off=0, y_off=0):
        text = self.font.render(self.content, True, (0,0,0))

        if self.parent == False:
            screen.blit(text, (self.x + x_off, self.y + y_off))
        else:
            screen.blit(text, ((self.actual_x + (self.parent.get_w() - self.w) + (self.w - self.parent.get_w()) // 2) + x_off,
                              (self.actual_y) + y_off))
    
    def update(self):
        if self.parent != False:
            self.actual_x = self.parent.get_actual_x() + self.x
            self.actual_y = self.parent.get_actual_y() + self.y
        else:
            self.actual_x = self.x
            self.actual_y = self.y

    def set_content(self, content):
        self.content = content

    def get_content(self):
        return self.content

    def set_font(self, font):
        self.font = font

    def get_font(self):
        return self.font

class Container(Element):
    children = []
    align_modes = Enum("align_modes", ["left", "center", "right"])
    align_mode = align_modes.center
    invisible = False
    color = (0, 100, 0)
    w = 0
    h = 0


    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.actual_x = x - w // 2
        self.actual_y = y - h // 2
        self.w = w 
        self.h = h 
        self.center_origin = True
        self.children = []

    def add_child(self, element):
        self.children.append(element)
        element.set_parent(self)

    def add_child_at(self, element, pos):
        if pos < 0:
            raise Exception("add_child_at called with negative pos argument")
        elif pos >= len(children):
            self.children.append(element)
        else:
            self.children.insert(pos, element)
        element.set_parent(self)

    def draw(self, screen, x_off=0, y_off=0):
        if not self.invisible:
            pygame.draw.rect(screen, 
                             self.color,
                             pygame.Rect(self.actual_x + x_off,
                                         self.actual_y + y_off,
                                         self.w,
                                         self.h))
        self.draw_children(screen, x_off, y_off)

    def draw_children(self, screen, x_off=0, y_off=0):
        prev_child_h_sum = 0
        for child in self.children:
            child.draw(screen, x_off, prev_child_h_sum + y_off)
            prev_child_h_sum += child.get_h()

    def update(self):
        for child in self.children:
            child.update()


class Button(Element):
    selected = False
    label = False

    def __init__(self, x=0, y=0, label = False):
        super().__init__(x,y)
        self.label = label

    def draw(self, screen):
        pass





