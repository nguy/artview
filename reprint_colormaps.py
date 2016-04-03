import numpy as np
import matplotlib.pyplot as plt
import pyart

cmap_list = ["pyart_" + m for m in pyart.graph.cm.datad
                         if not m.endswith("_r")]
nrows = len(cmap_list)
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

# borrows from colormaps_reference matplotlib example
fig, axes = plt.subplots(nrows=nrows, figsize=(8, 8))
fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
axes[0].set_title('Py-ART colormaps', fontsize=14)

axl = []

for ax, name in zip(axes, cmap_list):
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
    pos = list(ax.get_position().bounds)
    x_text = pos[0] - 0.01
    y_text = pos[1] + pos[3]/2.
    fig.text(x_text, y_text, name, va='center', ha='right', fontsize=10)
    axl.append((ax,name))

# Turn off *all* ticks & spines, not just the ones with colormaps.
for ax in axes:
    ax.set_axis_off()

for ax, name in axl:
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig('artview/icons/colormaps/%s.png' % name, dpi=20, bbox_inches=extent)

fig.show()