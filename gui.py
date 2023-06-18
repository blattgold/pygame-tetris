from enum import Enum
import pygame
import functools

class Element:
    x = 0
    y = 0
    actual_x = 0
    actual_y = 0
    w = 1
    h = 1
    parent = False # False = top level, no parent
    center_origin = False
    color = (0,0,0)
    invisible = False

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_actual_x(self):
        return self.actual_x

    def get_actual_y(self):
        return self.actual_y

    def set_actual_x(self, x):
        self.actual_x = x

    def set_actual_y(self, y):
        self.actual_y = y

    def set_x(self, x):
        self.x = x
        return self

    def set_y(self, y):
        self.y = y
        return self

    def get_h(self):
        return self.h

    def get_w(self):
        return self.w

    def set_color(self, color):
        self.color = color
        return self

    def update(self):
        self.actual_x = self.x
        self.actual_y = self.y

        if self.parent != False:
            self.actual_x = self.parent.get_actual_x() + self.actual_x
            self.actual_y = self.parent.get_actual_y() + self.actual_y

        if self.center_origin:
            self.actual_x = self.actual_x - self.w // 2
            self.actual_y = self.actual_y - self.h // 2

    def draw(self, x_off=0, y_off=0):
        pass

    def set_parent(self, element):
        self.parent = element

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
        text = self.font.render(self.content, True, self.color)

        screen.blit(text, (self.actual_x + x_off,
                              (self.actual_y) + y_off))
    
    def update(self):
        super().update()

    def set_content(self, content):
        self.content = content
        return self

    def get_content(self):
        return self.content

    def set_font(self, font):
        self.font = font
        return self

    def get_font(self):
        return self.font

class AbstractBox(Element):
    align_modes = Enum("align_modes", ["left", "center", "right"])
    align_mode = align_modes.center
    border_w = 0
    border_color = (0,0,0)
    corner_roundness = 0
    padding = (0,0,0,0)

    def __init__(self, x=0, y=0):
        super().__init__(x,y)

    def draw(self, screen, x_off=0, y_off=0):
        self.actual_x += x_off
        self.actual_y += y_off
        if not self.invisible:
            pygame.draw.rect(screen, 
                             self.color,
                             pygame.Rect(self.actual_x,
                                         self.actual_y,
                                         self.w,
                                         self.h),
                             0,
                             self.corner_roundness)
            if self.border_w > 0:
                pygame.draw.rect(screen,
                                 self.border_color,
                                 pygame.Rect(self.actual_x,
                                             self.actual_y,
                                             self.w,
                                             self.h),
                                 self.border_w,
                                 self.corner_roundness)

    def update(self):
        super().update()

    def set_border_w(self, w):
        self.border_w = w
        return self

    def set_border_color(self, color):
        self.border_color = color
        return self

    def set_corner_roundness(self, roundness):
        self.corner_roundness = roundness
        return self

    def set_padding(self, padding):
        self.padding = padding
        return self


class Container(AbstractBox):
    children = []

    def __init__(self, x=0, y=0):
        super().__init__(x,y)
        self.center_origin = True
        self.children = []

    def add_child(self, element):
        self.children.append(element)
        element.set_parent(self)
        return element

    def add_child_at(self, element, pos):
        if pos < 0:
            raise Exception("add_child_at called with negative pos argument")
        elif pos >= len(children):
            self.children.append(element)
        else:
            self.children.insert(pos, element)
        element.set_parent(self)
        return self

    def draw(self, screen, x_off=0, y_off=0):
        super().draw(screen, x_off, y_off)

        prev_child_h_sum = 0 + self.padding[0] 
        for child in self.children:
            child.set_actual_y(child.get_actual_y() + prev_child_h_sum)

            if self.align_mode == self.align_modes.left:
                child.draw(screen, x_off + self.padding[3], y_off)
            elif self.align_mode == self.align_modes.right:
                child.draw(screen, x_off + (self.w - child.get_w()) - self.padding[1], y_off)
            elif self.align_mode == self.align_modes.center:
                child.draw(screen, x_off + (self.w - child.get_w() // 2) - self.w // 2, y_off)

            prev_child_h_sum += child.get_h()

    def update(self):

        self.h = 0
        self.w = 0

        highest_child_w = 0
        for child in self.children:
            self.h += child.get_h()
            if highest_child_w < child.get_w():
                highest_child_w = child.get_w()
                self.w = child.get_w()

        self.h += self.padding[0] + self.padding[2]
        self.w += self.padding[1] + self.padding[3]

        super().update()

        for child in self.children:
            child.update()




class Button(AbstractBox):
    selected = False
    child_label = False

    def __init__(self, label, x=0, y=0):
        super().__init__(x,y)
        self.align_mode = self.align_modes.left
        self.child_label = label
        label.set_parent(self)

    def draw(self, screen, x_off, y_off):
        super().draw(screen, x_off, y_off)

        self.child_label.set_actual_y(self.actual_y + self.child_label.get_y())
        self.child_label.set_actual_x(self.actual_x + self.child_label.get_x())
        if self.align_mode == self.align_modes.left:
            self.child_label.draw(screen, 0 + self.padding[3], 0 + self.padding[0])

    def update(self):
        super().update()
        self.child_label.update()
        self.h = self.child_label.get_h() + self.padding[0] + self.padding[2]
        self.w = self.child_label.get_w() + self.padding[1] + self.padding[3]





