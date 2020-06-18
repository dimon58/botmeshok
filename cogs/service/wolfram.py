import matplotlib
# import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

session = WolframLanguageSession()


class nat_lang_out_line():
    def __init__(self, content=None, is_this_a_file=False, HoldComplete=False):
        self.content = content
        self.is_this_a_file = is_this_a_file
        self.HoldComplete = HoldComplete


async def nat_lang(cmd):  # Wolfram's natural language
    res = session.evaluate(wl.WolframAlpha(cmd))
    first = True
    first_different = False
    output = f'Input: {res[0][1]}\n'
    for rule in res[1:]:
        if first:
            label = rule[0][0][0]
            # print(label)
            first = False
        # print(rule[0][0][0],rule[1])
        if rule[0][0][0] == label:
            output += str(rule[1]) + '\n'
        else:
            break

    return output


async def nat_lang_full(cmd):  # Wolfram's natural language
    res = session.evaluate(wl.WolframAlpha(cmd))
    output = ''
    for rule in res:
        # output += str(rule[1]) + '\n'
        output += str(rule[0][0][0]) + ': ' + str(rule[1]) + '\n'
        if 'Plot' in str(rule[0][0][0]):
            ex = rule[1][0]
            wolframplot_to_png(ex)

    print()
    print()
    print()
    print()
    print()

    return output + '\n' + str(res)


async def nat_lang_full_no_HoldComplete(cmd: str) -> list:  # Wolfram's natural language
    res = session.evaluate(wl.WolframAlpha(cmd))
    output = []
    # for rule in res: print(rule)
    for rule in res:
        output_line = nat_lang_out_line()
        output_line.HoldComplete = 'HoldComplete' in str(rule)
        if 'Plot' in str(rule):
            output_line.is_this_a_file = True
            ex = rule[1][0]
            output_line.content = await wolframplot_to_png(ex, str(rule[0]) + '.png')
        else:
            output_line.content = str(rule[0][0][0]) + ': ' + str(rule[1])
        output.append(output_line)
    return output


async def nat_lang_full_no_HoldComplete_copy(cmd):  # Wolfram's natural language
    res = session.evaluate(wl.WolframAlpha(cmd))
    output = ''
    output_plots = []
    is_plots = False
    # for rule in res: print(rule)
    for rule in res:
        if 'HoldComplete' not in str(rule):
            output += str(rule[0][0][0]) + ': ' + str(rule[1]) + '\n'
        else:
            if 'Plot' in str(rule):
                is_plots = True
                ex = rule[1][0]
                output_plots.append(await wolframplot_to_png(ex, str(rule[0]) + '.png'))
    if is_plots:
        return [output, output_plots]
    else:
        return [output, None]


async def draw_plot(func: str, lim_left: int, lim_right: int, outfile='out.png'):
    s = f'Plot[{func},'
    s += '{x,'
    s += f'{lim_left},{lim_right}'
    s += '}]'
    # return session.evaluate(wlexpr(s))
    r = session.evaluate(wlexpr(s))
    mas = np.array(r[0][0][0][2][0][1][0])
    color = tuple(r[0][0][0][2][0][0][1])
    matplotlib.rcParams.update({'font.size': 20})
    pylab.figure(figsize=(18, 18), dpi=80, facecolor='w', edgecolor='k')
    pylab.plot(mas[:, 0], mas[:, 1], color=tuple(r[0][0][0][2][0][0][1]), linewidth=r[0][0][0][2][0][0][2][0])
    pylab.grid()
    pylab.title(func, fontsize=30)
    pylab.savefig('temp/'+outfile)
    return outfile


async def wolframplot_to_png(ex, out_file_name='outfile.png'):
    title = ex[0]
    ex = str(ex).replace('(', '{').replace(')', '}')
    r = await expression(ex)
    # print(r)
    mas = np.ndarray((0, 2))
    mas_for_drawing = []
    RGBColor = tuple(r[0][0][0][2][0][0][1])
    linewidth = r[0][0][0][2][0][0][2][0]
    for i in r[0][0][0][2][0]:
        temp = np.array(i[0])
        if temp.shape[-1] == 2:
            mas = np.concatenate([mas, temp], axis=0)
            mas_for_drawing.append(temp)
            # pylab.plot(temp[:, 0], temp[:, 1], color='blue')
    dx = mas[:, 0].max() - mas[:, 0].min()
    dy = mas[:, 0].max() - mas[:, 0].min()
    r = dx + dy
    dx *= 40 / r
    dy *= 40 / r
    matplotlib.rcParams.update({'font.size': 35})
    pylab.figure(figsize=(dx, dy), dpi=50, facecolor='w', edgecolor='k')
    for i in mas_for_drawing:
        pylab.plot(i[:, 0], i[:, 1], color=RGBColor, linewidth=5)
    pylab.grid(linewidth=3)
    # pylab.title(title, fontsize=40)
    pylab.savefig('temp/'+out_file_name)
    return 'temp/'+out_file_name


async def expression(s: str):
    return session.evaluate(wlexpr(s))

