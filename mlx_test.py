from mlx import Mlx

m = Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, 400, 300, "Metin Testi")

def redraw(param):
    m.mlx_string_put(mlx_ptr, win_ptr, 50, 50, 0xFFFFFFFF, "Merhaba MLX")

def on_close(param):
    m.mlx_loop_exit(mlx_ptr)

m.mlx_loop_hook(mlx_ptr, redraw, None)
m.mlx_hook(win_ptr, 33, 0, on_close, None)
m.mlx_loop(mlx_ptr)