import numpy as np
import matplotlib.pyplot as plt
import pdb

def hide_top_right(ax):
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	ax.yaxis.set_ticks_position('left')
	ax.xaxis.set_ticks_position('bottom')

# Data and model types
probtype_colors = ['mediumseagreen', 'darkturquoise']
legend_text = ['3 Disks', '4 Disks']
model_names = ['Zero-shot', 'ICL', 'Zero-shot\n+\nMonitor', 'ICL\n+\nMonitor']
frac_solved_without_invalid = np.array([[0.0, 0.01],[0.29, 0.06],[0.42, 0.11],[0.46, 0.27]])
frac_invalid_moves = np.array([[0.24, 0.61], [0.19, 0.29], [0.005, 0.16], [0.03, 0.08]])
avg_reward = np.array([[-72.85, -321.41],[15.62, -147],[13.31, -113.85],[23.12, -50.83]])

# Plot settings
total_bar_width = 0.8
ind_bar_width = total_bar_width / 2
x_pts = np.arange(len(model_names))
title_font = 16
axis_label_font = 14
tick_font = 14
legend_font = 14

# Plot fraction solved
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_solved_without_invalid[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_solved_without_invalid[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
plt.xticks(np.arange(len(model_names)), model_names, fontsize=axis_label_font)
hide_top_right(ax)
plt.title('Solution rate (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_solved.png',dpi=300)
plt.close()

# Plot fraction invalid
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_invalid_moves[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_invalid_moves[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(len(model_names)), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Invalid move rate (' + r'$\downarrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_invalid.png',dpi=300)
plt.close()

# Plot average reward
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), avg_reward[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width, zorder=0)
plt.bar(x_pts + (ind_bar_width/2), avg_reward[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width, zorder=1)
plt.plot([0,0],[0,0], linestyle='dashed', color='gray', zorder=2)

legend_text = ['Optimal', '3 Disks', '4 Disks']
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.plot([-0.5,3.5], [95.15, 95.15], linestyle='dashed', color=probtype_colors[0], label='_nolegend_')
plt.plot([-0.5,3.5], [89.88, 89.88], linestyle='dashed', color=probtype_colors[1], label='_nolegend_')
plt.ylim([-350,120])
plt.yticks(fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(len(model_names)), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Average reward (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./avg_reward.png',dpi=300)
plt.close()





# Data and model types
probtype_colors = ['mediumseagreen', 'darkturquoise']
legend_text = ['3 Disks', '4 Disks']
model_names = ['Zero-shot', 'ICL', ' \n \n ',' \n \n ']
frac_solved_without_invalid = np.array([[0.0, 0.01],[0.29, 0.06]])
frac_invalid_moves = np.array([[0.24, 0.61], [0.19, 0.29]])
avg_reward = np.array([[-72.85, -321.41],[15.62, -147]])

# Plot settings
total_bar_width = 0.8
ind_bar_width = total_bar_width / 2
x_pts = np.arange(2)
title_font = 16
axis_label_font = 14
tick_font = 14
legend_font = 14

# Plot fraction solved
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_solved_without_invalid[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_solved_without_invalid[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
hide_top_right(ax)
plt.title('Solution rate (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_solved_noICL.png',dpi=300)
plt.close()

# Plot fraction invalid
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_invalid_moves[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_invalid_moves[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Invalid move rate (' + r'$\downarrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_invalid_noICL.png',dpi=300)
plt.close()

# Plot average reward
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), avg_reward[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width, zorder=0)
plt.bar(x_pts + (ind_bar_width/2), avg_reward[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width, zorder=1)
plt.plot([0,0],[0,0], linestyle='dashed', color='gray', zorder=2)

legend_text = ['Optimal', '3 Disks', '4 Disks']
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.plot([-0.5,3.5], [95.15, 95.15], linestyle='dashed', color=probtype_colors[0], label='_nolegend_')
plt.plot([-0.5,3.5], [89.88, 89.88], linestyle='dashed', color=probtype_colors[1], label='_nolegend_')
plt.ylim([-350,120])
plt.yticks(fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Average reward (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./avg_reward_noICL.png',dpi=300)
plt.close()




# Data and model types
probtype_colors = ['mediumseagreen', 'darkturquoise']
legend_text = ['3 Disks', '4 Disks']
model_names = ['Zero-shot', '', ' \n \n ',' \n \n ']
frac_solved_without_invalid = np.array([[0.0, 0.01]])
frac_invalid_moves = np.array([[0.24, 0.61]])
avg_reward = np.array([[-72.85, -321.41]])

# Plot settings
total_bar_width = 0.8
ind_bar_width = total_bar_width / 2
x_pts = np.arange(1)
title_font = 16
axis_label_font = 14
tick_font = 14
legend_font = 14

# Plot fraction solved
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_solved_without_invalid[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_solved_without_invalid[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
hide_top_right(ax)
plt.title('Solution rate (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_solved_ZSonly.png',dpi=300)
plt.close()

# Plot fraction invalid
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), frac_invalid_moves[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width)
plt.bar(x_pts + (ind_bar_width/2), frac_invalid_moves[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width)
plt.ylim([0,1])
plt.yticks([0,0.2,0.4,0.6,0.8,1],['0','0.2','0.4','0.6','0.8','1'],fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Invalid move rate (' + r'$\downarrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./frac_invalid_ZSonly.png',dpi=300)
plt.close()

# Plot average reward
ax = plt.subplot(111)
plt.bar(x_pts - (ind_bar_width/2), avg_reward[:,0], color=probtype_colors[0], edgecolor='black', width=ind_bar_width, zorder=0)
plt.bar(x_pts + (ind_bar_width/2), avg_reward[:,1], color=probtype_colors[1], edgecolor='black', width=ind_bar_width, zorder=1)
plt.plot([0,0],[0,0], linestyle='dashed', color='gray', zorder=2)

legend_text = ['Optimal', '3 Disks', '4 Disks']
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.plot([-0.5,3.5], [95.15, 95.15], linestyle='dashed', color=probtype_colors[0], label='_nolegend_')
plt.plot([-0.5,3.5], [89.88, 89.88], linestyle='dashed', color=probtype_colors[1], label='_nolegend_')
plt.ylim([-350,120])
plt.yticks(fontsize=tick_font)
# plt.ylabel('Fraction solved problems (without invalid moves)',fontsize=axis_label_font)
plt.xticks(np.arange(4), model_names, fontsize=axis_label_font)
plt.xlim([-0.5,3.5])
hide_top_right(ax)
plt.title('Average reward (' + r'$\uparrow$' + 'better)',fontsize=title_font)
plt.legend(legend_text,frameon=False,bbox_to_anchor=(1,1),fontsize=legend_font)
plt.tight_layout()
# ax.set_aspect(2)
plt.savefig('./avg_reward_ZSonly.png',dpi=300)
plt.close()



