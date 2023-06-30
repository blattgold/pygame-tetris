from enum import Enum
import pygame
import copy
import string

class Element:
    x = 0
    y = 0
    actual_x = 0
    actual_y = 0
    w = 1
    h = 1
    parent = False # False = top level, no parent
    color = (0,0,0)
    invisible = False
    selectable = False
    center_origin = False
    debug = False
    first_update = True

    def __init__(self, x=0, y=0, center_origin=False):
        self.x = x
        self.y = y
        self.center_origin = center_origin

    def set_debug(self):
        self.debug = True
        return self

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

    def get_selectable(self):
        return self.selectable

    def update(self):
        if self.first_update:
            self.first_update = False
            self.update()

        self.actual_x = self.x
        self.actual_y = self.y

        if self.parent != False:
            self.actual_x += self.parent.get_actual_x()
            self.actual_y += self.parent.get_actual_y()

        if self.center_origin:
            self.actual_x = self.actual_x - self.w // 2
            self.actual_y = self.actual_y - self.h // 2

    def input(self, event, key_gui_up=pygame.K_w, key_gui_down=pygame.K_s, key_gui_action=pygame.K_RETURN):
        pass

    def draw(self, x_off=0, y_off=0):
        pass

    def set_parent(self, element):
        self.parent = element

    def get_centered(self):
        return self.center_origin

class Text(Element):
    content = False
    font = False

    def __init__(self, content, font, x=0, y=0, center_origin=False):
        super().__init__(x, y, center_origin)
        self.content = content
        self.font = font

    def draw(self, screen, x_off=0, y_off=0):
        text = self.font.render(self.content, True, self.color)

        screen.blit(text, (self.actual_x + x_off, self.actual_y + y_off))
    
    def update(self):
        super().update()
        self.w = int(self.font.render(self.content, True, (0,0,0)).get_width())
        self.h = int(self.font.render(self.content, True, (0,0,0)).get_height())

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

class BoxElement(Element):
    align_modes = Enum("align_modes", ["left", "center", "right"])
    align_mode = align_modes.right
    border_w = 0
    border_color = (0,0,0)
    corner_roundness = 0
    padding = (0,0,0,0)

    def __init__(self, x=0, y=0, center_origin=False):
        super().__init__(x,y,center_origin)
        self.border_w = 0
        self.border_color = (0,0,0)
        self.corner_roundness = 0
        self.padding = (0,0,0,0)

    def draw(self, screen, x_off=0, y_off=0):
        if not self.invisible:
            pygame.draw.rect(screen, 
                             self.color,
                             pygame.Rect(self.actual_x + x_off,
                                         self.actual_y + y_off,
                                         self.w,
                                         self.h),
                             0,
                             self.corner_roundness)
            if self.border_w > 0:
                pygame.draw.rect(screen,
                                 self.border_color,
                                 pygame.Rect(self.actual_x + x_off,
                                             self.actual_y + y_off,
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


class Container(BoxElement):
    children = []
    child_spacing = 0

    def __init__(self, x=0, y=0, center_origin=True):
        super().__init__(x,y,center_origin)
        self.children = []
        self.align_mode = self.align_modes.center
        self.default_style()

    def default_style(self):
        self.set_border_w(3) \
        .set_border_color((160,160,160)) \
        .set_color((200,200,200)) \
        .set_corner_roundness(10) \
        .set_padding((10,10,10,10)) \
        .set_child_spacing(5) 

    def set_child_spacing(self, spacing):
        self.child_spacing = spacing
        return self

    def get_child(self, index):
        return self.children[index]

    def add_child(self, element):
        self.children.append(element)
        element.set_parent(self)
        return self

    def add_child_at(self, element, pos):
        if pos < 0:
            raise Exception("add_child_at called with negative pos argument")
        elif pos >= len(children):
            self.children.append(element)
        else:
            self.children.insert(pos, element)
        element.set_parent(self)
        return self

    def input(self, event, key_gui_up=pygame.K_w, key_gui_down=pygame.K_s, key_gui_action=pygame.K_RETURN):
        if event.type == pygame.KEYDOWN:
            if event.key == key_gui_up:
                self.update_selected(-1)
            if event.key == key_gui_down:
                self.update_selected(1)
            if event.key == key_gui_action:
                if self.get_selected() != False:
                    self.get_selected()[1].on_click()

        for child in self.children:
            child.input(event)

    def draw(self, screen, x_off=0, y_off=0):
        super().draw(screen, x_off, y_off)

        for child in self.children:
            child.draw(screen, x_off, y_off)

    def update(self):
        super().update()

        self.h = 0
        self.w = 0

        '''
        update all children
        '''
        for child in self.children:
            child.update()

        '''
        set width to highest child width
        '''
        for child in self.children:
            if child.get_w() > self.w:
                self.w = child.get_w()
        '''
        add up height of all children + spacing
        '''
        prev_children_h = 0
        for child_index, child in enumerate(self.children):
            self.h += child.get_h()

            if child_index != 0 and child_index != len(self.children) - 1:
                self.h += self.child_spacing

            prev_children_h += self.child_spacing

            if self.align_mode == self.align_modes.left:
                child.set_actual_x(child.get_actual_x() + self.padding[3])
            elif self.align_mode == self.align_modes.right:
                child.set_actual_x(child.get_actual_x() + (self.w - child.get_w()) + self.padding[1])
            else: 
                child.set_actual_x(child.get_actual_x() + (self.w - child.get_w() // 2) - self.w // 2  + self.padding[3])

            child.set_actual_y(child.get_actual_y() + prev_children_h)

            prev_children_h += child.get_h()

        self.h += self.padding[0] + self.padding[2]
        self.w += self.padding[1] + self.padding[3]





    def update_selected(self, d):
        selectable = self.find_selectable()
        if selectable != False:
            if len(selectable) >= 1:
                current = self.get_selected(selectable)
                if current != False:
                    if current[0] + d < len(selectable) and current[0] + d >= 0:
                        current[1].set_selected(False)
                        selectable[(current[0]) + d].set_selected(True)
                else:
                    selectable[0].set_selected(True)

    def find_selectable(self):
        selectable = []
        for child in self.children:
            if child.get_selectable():
                selectable.append(child)
        if len(selectable) == 0:
            return False
        else:
            return selectable

    def get_selected(self, selectable=None):
        if selectable == None:
            selectable = self.find_selectable()
        if selectable == False:
            return False
        for s_index, s in enumerate(selectable):
            if s.get_selected():
                return (s_index, s)
        return False


class Button(BoxElement):
    selected = False
    child_label = False
    color_deselected = (0,0,0)
    color_selected = (0,0,0)
    on_click_fun = lambda self : print("unassigned button action")
    on_click_fun_args = []

    def __init__(self, label, x=0, y=0, center_origin=False):
        super().__init__(x,y,center_origin)
        self.selectable = True
        self.align_mode = self.align_modes.left
        self.child_label = label
        self.on_click_caller = self
        label.set_parent(self)
        self.default_style()

    def default_style(self):
        self.set_border_w(2) \
        .set_border_color((0,0,0)) \
        .set_color_deselected((100,100,100)) \
        .set_color_selected((100,200,100)) \
        .set_padding((5,10,5,10))

    def set_selected(self, selected):
        self.selected = selected
        return self

    def get_selected(self):
        return self.selected

    def set_color_deselected(self, color):
        self.color_deselected = color
        return self

    def set_color_selected(self,color):
        self.color_selected = color
        return self

    def draw(self, screen, x_off, y_off):
        super().draw(screen, x_off, y_off)

        self.child_label.draw(screen)

    def update(self):
        self.h = self.child_label.get_h() + self.padding[0] + self.padding[2]
        self.w = self.child_label.get_w() + self.padding[1] + self.padding[3]

        if self.selected:
            self.color = self.color_selected
        else:
            self.color = self.color_deselected

        self.child_label.update()
        self.child_label.set_actual_x(self.child_label.get_actual_x() + self.padding[3])
        self.child_label.set_actual_y(self.child_label.get_actual_y() + self.padding[0])

        super().update()



    def on_click(true_self):
        self = true_self.on_click_caller
        return true_self.on_click_fun(*(true_self.on_click_fun_args))

    def set_on_click(self,caller,fun,args):
        self.on_click_fun = fun
        self.on_click_caller = caller
        self.on_click_fun_args = args
        return self

class TextInput(BoxElement):
    input_text = False
    on_action_fun = lambda self : print("unassigned action")
    on_action_fun_args = []
    max_length = 0
    
    def __init__(self, input_text, max_length=20, x=0, y=0, center_origin=False):
        super().__init__(x, y, center_origin)
        self.input_text = input_text.set_content(input_text.get_content() + "_")
        input_text.set_parent(self)
        self.on_action_caller = self
        self.default_style()
        self.max_length = max_length

    def default_style(self):
        self.set_border_w(0) \
        .set_corner_roundness(10) \
        .set_padding((2,5,2,5)) \
        .set_border_color((0,0,0)) \
        .set_color((180,180,255))

    def update(self):
        self.input_text.update()
        self.input_text.set_actual_x(self.input_text.get_actual_x() + self.padding[3])
        self.input_text.set_actual_y(self.input_text.get_actual_y() + self.padding[0])

        self.w = self.input_text.get_w()
        self.h = self.input_text.get_h()

        self.w += self.padding[1] + self.padding[3]
        self.h += self.padding[0] + self.padding[2]
        
        super().update()
    
    def draw(self, screen, x_off=0, y_off=0):
        super().draw(screen, x_off, y_off)
        self.input_text.draw(screen)

    def get_input_text(self):
        cp = copy.copy(self.input_text)
        return cp.set_content(cp.get_content()[:-1])

    def get_len(self):
        return len(self.input_text) - 1

    def input(self, event, key_gui_up=pygame.K_w, key_gui_down=pygame.K_s, key_gui_action=pygame.K_RETURN):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.input_text.get_content()) > 1:
                    self.input_text.set_content(self.input_text.get_content()[:-2] + "_")
            elif event.key == key_gui_action:
                self.on_action()
            elif len(self.input_text.get_content()) < self.max_length - 1:
                self.input_text.set_content(self.input_text.get_content()[:-1])
                self.input_text.set_content(self.input_text.get_content() + event.unicode + "_")

    def on_action(true_self):
        self = true_self.on_action_caller
        return true_self.on_action_fun(*(true_self.on_action_fun_args))

    def set_on_action(self,caller,fun,args):
        self.on_action_fun = fun
        self.on_action_caller = caller
        self.on_action_fun_args = args
        return self


