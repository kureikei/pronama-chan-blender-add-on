bl_info = {
    "name": "Pronama-chan",
    "author": "KUREI Kei",
    "version": (1, 0),
    "blender": (2, 67, 0),
    "location": "3D View > Spacebar Menu > Pronama-chan",
    "description": "Esc to quit, restart via spacebar menu",
    "category": "3D View"}

import bpy
import os.path
import random
from math import radians, degrees
from mathutils import Vector
from bgl import *

# スプライトオブジェクトのリスト
sprites = []

SPRITE_MAX = 50 # スプライトオブジェクトの数
TEXTURE_SIZE = 256 # テクスチャの幅 (pixel)

# テクスチャの UV テーブル
spriteUV = ((0,     0, 0.125, 0.1875),
            (0.125, 0, 0.125, 0.1875),
            (0.25,  0, 0.125, 0.1875),
            (0.375, 0, 0.125, 0.1875),
            (0.5,   0, 0.125, 0.1875),
            (0.625, 0, 0.125, 0.1875))

# スプライト制御
class PronamaChanSprite:

    # 開始設定（今回の場合、x 座標の初期値だけ外部から指定する）
    def setup(self, x):
        self.x = x
        self.y = random.random()
        self.current_index = random.randint(0, len(spriteUV) - 1)
        self.scale = 1 # テクスチャ画像のスケール（1倍にすると画面の縦幅の大きさで描画される）

    # 更新処理（描画ごとに呼ばれる）
    def update(self, aspect):
        # スプライトインデックス更新
        self.current_index += 1
        if self.current_index >= len(spriteUV):
            self.current_index = 0

        # 移動
        self.x -= 0.015 * aspect # 0.015 は移動量
        if self.x <= 0:
            # 左側に移動したら位置を再設定
            self.setup(1 + self.scale * 0.125 * aspect) # 0.125 はテクスチャ内でのキャラの横幅


# ビューポートの設定
def view_setup():    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glOrtho(0, 1, 0, 1, -15, 15)
    gluLookAt(0.0, 0.0, 1.0, 0.0,0.0,0.0, 0.0,1.0,0.0)
    
# ビューポートを viewport でリセット
def view_reset(viewport):
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glViewport(viewport[0], viewport[1], viewport[2], viewport[3])

# スプライトの描画
def draw_sprite(sprite, region):
    aspect = region.height / region.width

    # スプライト更新
    sprite.update(aspect) 

    # UV 情報
    i = sprite.current_index
    global spriteUV
    sprtU = spriteUV[i][0]
    sprtV = spriteUV[i][1]
    sprtW = spriteUV[i][2]
    sprtH = spriteUV[i][3]

    # 頂点情報
    vertW = sprtW * sprite.scale * aspect
    vertH = sprtH * sprite.scale
    x = sprite.x
    y = sprite.y

    # 頂点
    coordinates = [(x, y), (x - vertW, y), (x - vertW, y - vertH), (x, y - vertH)]
    verts = coordinates

    # UV
    tex_coords = [((sprtU + sprtW), (sprtV + sprtH)), (sprtU, (sprtV + sprtH)), (sprtU, sprtV), ((sprtU + sprtW), sprtV)]

    # ポリゴン描画設定
    glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)
    
    # テクスチャ描画設定
    glEnable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, Storage._texture1[0])
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, TEXTURE_SIZE, TEXTURE_SIZE, 0, GL_RGBA, GL_FLOAT, Storage.data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, 33071)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, 33071)

    # ポリゴンを描画
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    
    glTexCoord2f(tex_coords[0][0],tex_coords[0][1])
    glVertex2f(verts[0][0],verts[0][1])
    glTexCoord2f(tex_coords[1][0],tex_coords[1][1])
    glVertex2f(verts[1][0],verts[1][1])
    glTexCoord2f(tex_coords[2][0],tex_coords[2][1])
    glVertex2f(verts[2][0],verts[2][1])
    glTexCoord2f(tex_coords[3][0],tex_coords[3][1])
    glVertex2f(verts[3][0],verts[3][1])
    
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glDisable(GL_BLEND)
        
# 描画コールバック
def draw_callback_px(self, context):
    if self.__class__._pointer != context.area.as_pointer():
        return

    # 描画領域
    if not context.region:
        return

    # 現在のビューポートを退避
    viewport = Buffer(GL_INT, 4)
    glGetIntegerv(GL_VIEWPORT, viewport)

    # ビューポート設定
    view_setup()

    # スプライトの描画
    for s in sprites:
        if s is not None:
            draw_sprite(s, context.region)

    # ビューポートを元に戻す
    view_reset(viewport)

    # OpenGL 設定をデフォルトに戻す
    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)


# データ管理用
class Storage:
    _texture1 = None  # OpenGL テクスチャ管理 ID
    data = None       # テクスチャバイナリデータ


# Blender アドオン オペレータクラス
# * VIEW3D_OT_* という名前でクラスを宣言する
# * bpy.types.Operator を継承する
class VIEW3D_OT_pronama_chan(bpy.types.Operator):
    bl_idname = "view3d.pronama_chan"
    bl_label = "Pronama-chan"
    
    _handle = None
    _pointer = None
    _area = None
    _timer = None

    # イベント処理
    def modal(self, context, event):
        if (self.__class__._area is None or not any(a == self.__class__._area for a in context.screen.areas)):
            self.end(context)
            return {'FINISHED'}
        
        # タイマーイベント
        if event.type == 'TIMER':
            # 画面更新
            self.__class__._area.tag_redraw()

        # ESC キーイベント
        elif event.type in {'ESC'}:
            self.end(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    # 終了処理
    @classmethod
    def end(cls, context):
        sprites = None

        try:
            if cls._handle is not None:
                bpy.types.SpaceView3D.draw_handler_remove(cls._handle, 'WINDOW')
        except:
            pass

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        try:
            context.window_manager.event_timer_remove(cls._timer)
        except TypeError:
            pass
            
        cls._timer = None
        cls._pointer = None
        cls._area = None

    def invoke(self, context, event):
        if self.__class__._area is not None:
            self.end(context)
        
        area = context.area
        if area.type != 'VIEW_3D':
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    break
            else:
                area = None
                
        if area is not None:
            # テクスチャ管理 ID をを生成
            Storage._texture1 = Buffer(GL_INT, 1)
            glGenTextures(1, Storage._texture1)

            self.__class__._pointer = area.as_pointer()
            self.__class__._area = area
            
            # 描画コールバックに渡される引数
            args = (self, context)

            # 描画コールバックを登録
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            VIEW3D_OT_pronama_chan._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            area.tag_redraw()
            
            try:
                context.window_manager.event_timer_remove(self.__class__._timer)
            except TypeError:
                pass
            self.__class__._timer = context.window_manager.event_timer_add(0.1, context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


# ファイルを読み込んでバイナリデータを buffer に格納
def load_image_to_buffer(filepath, buffer):
    img = bpy.data.images.load(filepath)
    buffer[:] = img.pixels[:]
    img.user_clear()
    bpy.data.images.remove(img)
    del img

# アドオン初期化
def init(scene):
    bpy.app.handlers.scene_update_post.remove(init)
    
    # スプライトオブジェクト生成
    for i in range(0, SPRITE_MAX):
        s = PronamaChanSprite()
        s.setup(1 + 0.2 * i) # 適当にずらす
        sprites.append(s)

    # テクスチャバッファを確保
    Storage.data = Buffer(GL_FLOAT, TEXTURE_SIZE * TEXTURE_SIZE * 4)
    
    # テクスチャ画像を読み込んでバイナリデータをバッファに入れる
    folder = os.path.dirname(__file__) + os.path.sep
    load_image_to_buffer(folder + "texture.png", Storage.data)

# アドオン登録
def register():
    bpy.app.handlers.scene_update_post.append(init)
    bpy.utils.register_class(VIEW3D_OT_pronama_chan)

# アドオン登録解除
def unregister():
    VIEW3D_OT_pronama_chan.end(bpy.context)
    bpy.utils.unregister_class(VIEW3D_OT_pronama_chan)

if __name__ == "__main__":
    register()
