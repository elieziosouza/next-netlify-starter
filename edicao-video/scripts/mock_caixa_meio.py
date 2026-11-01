"""Teste da caixa de manchete no meio da tela: na tela dividida ela fica em cima da emenda; em tela cheia, abaixo do queixo."""
import sys, importlib.util
from PIL import Image
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rc", f"{S}/work/render_curitiba.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work"); import barra_lateral as B; B.FD = R.FD
s = R.segs[1]; tt = s["t0"] + 1.2
A = R.split_scene(tt, s, -10.0)                                   # tempo fora das legendas: só a imagem
B.draw_bar(A, 0.35, "canal"); A.alpha_composite(R.top)
B.lower_card(A, "ELEIÇÕES 2026", ["ATAQUE EM CURITIBA:", "CARRO COM ADESIVO DO PT"], R.SEAM - 120, 1.0)
import numpy as np
me = R.me_src(18.6).copy(); C = Image.fromarray(me).convert("RGBA"); B.draw_bar(C, 0.7, "canal"); C.alpha_composite(R.top)
B.lower_card(C, "ELEIÇÕES 2026", ["PESQUISA VOX BRASIL:", "LULA 51% x 49% FLÁVIO"], 1600, 1.0)
sheet = Image.new("RGB", (1080, 960)); [sheet.paste(o.convert("RGB").resize((540, 960)), (i * 540, 0)) for i, o in enumerate((A, C))]
sheet.save(f"{S}/v31/caixa_meio.jpg", quality=92); print("ok")
