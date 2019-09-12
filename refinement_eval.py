"""
Calculates the best performing parameter values with given testing data as specified in file
Autocalibration-Parametersweep-Testing.xlsx
"""
import sys, re, argparse, os, subprocess as sp, warnings, numpy as np, math
# import modin.pandas as pd
import pandas as pd
#from jinja2 import Template as ji
import jinja2 as ji
import ruamel.yaml as yaml
from usac_eval import ji_env, get_time_fixed_kp, insert_opt_lbreak, prepare_io

def filter_nr_kps_calc_t(**vars):
    tmp = vars['data'].loc[vars['data']['nrTP'] == '100to1000'].copy(deep=True)
    linref = tmp['linRefinement_us']
    ba = tmp['bundleAdjust_us']
    tmp['linRef_BA_us'] = linref + ba
    return tmp

def get_best_comb_scenes_1(**keywords):
    if 'res_par_name' not in keywords:
        raise ValueError('Missing parameter res_par_name')
    from usac_eval import pars_calc_single_fig_partitions
    ret = pars_calc_single_fig_partitions(**keywords)
    # if len(ret['partitions']) != 2:
    #     raise ValueError('Only a number of 2 partitions is allowed in function get_best_comb_scenes_1')
    b_new_index = ret['b'].stack().reset_index()
    if len(ret['it_parameters'])  > 1:
        it_pars_name = '-'.join(ret['it_parameters'])
    else:
        it_pars_name = ret['it_parameters'][0]
    b_mean_l = []
    drops = []
    for i, val in enumerate(ret['partitions']):
        drops.append([val1 for i1, val1 in enumerate(ret['partitions']) if i1 != i])
        drops[-1] += [ret['grp_names'][-1]]
        b_mean_l.append(b_new_index.drop(drops[-1], axis=1).groupby(ret['it_parameters'] + [val]).mean())
    drops.append(ret['partitions'])
    b_mean_l.append(b_new_index.drop(drops[-1], axis=1).groupby(ret['it_parameters'] +
                                                                        [ret['grp_names'][-1]]).mean())
    data_parts = ret['partitions'] + [ret['grp_names'][-1]]
    data_it_indices = []
    data_it_b_columns = []
    column_legend = []
    b_mean_name = []
    part_name_title = []
    is_numeric = []
    from statistics_and_plot import replaceCSVLabels, tex_string_coding_style, calcNrLegendCols, strToLower, compile_tex
    tex_infos = {'title': 'Mean Combined R \\& t Errors Over Different Properties ' +
                          ' for Parameter Variations of ' + ret['sub_title_it_pars'],
                 'sections': [],
                 # Builds an index with hyperrefs on the beginning of the pdf
                 'make_index': True,
                 # If True, the figures are adapted to the page height if they are too big
                 'ctrl_fig_size': True,
                 # If true, a pdf is generated for every figure and inserted as image in a second run
                 'figs_externalize': False,
                 # If true and a bar chart is chosen, the bars a filled with color and markers are turned off
                 'fill_bar': True,
                 # Builds a list of abbrevations from a list of dicts
                 'abbreviations': ret['gloss']
                 }
    for i, (df, dp) in enumerate(zip(b_mean_l, data_parts)):
        tmp = df.reset_index().set_index(ret['it_parameters'])
        if len(ret['it_parameters']) > 1:
            data_it_indices.append(['-'.join(a) for a in tmp.index])
            tmp.index = data_it_indices[-1]
            tmp.index.name = it_pars_name
        else:
            data_it_indices.append([str(a) for a in tmp.index])
        is_numeric.append(pd.to_numeric(tmp[dp], errors='coerce').notnull().all())
        tmp = tmp.reset_index().set_index([dp] + [it_pars_name]).unstack(level=-1)
        column_legend.append([tex_string_coding_style(b) for a in tmp.columns for b in a if b in data_it_indices[-1]])
        data_it_b_columns.append(['-'.join([str(b) if b in data_it_indices[-1] else 'b_mean'
                                           for b in a]) for a in tmp.columns])
        tmp.columns = data_it_b_columns[-1]

        b_mean_name.append('data_mean_RTerrors_over_' + '-'.join(map(str, drops[i])) + '_vs_' + str(dp) +
                           '_for_opts_' + '-'.join(ret['it_parameters']) + '.csv')
        fb_mean_name = os.path.join(ret['tdata_folder'], b_mean_name[-1])
        with open(fb_mean_name, 'a') as f:
            f.write('# Mean combined R & t errors (b_min) over properties ' + '-'.join(map(str, drops[i])) +
                    ' compared to ' + str(dp) + ' for options ' +
                    '-'.join(ret['it_parameters']) + '\n')
            tmp.to_csv(index=True, sep=';', path_or_buf=f, header=True, na_rep='nan')

        part_name_title.append('')
        len_drops = len(drops[i])
        for i1, val in enumerate(drops[i]):
            part_name_title[-1] += replaceCSVLabels(val, True)
            if (len_drops <= 2):
                if i1 < len_drops - 1:
                    part_name_title[-1] += ' and '
            else:
                if i1 < len_drops - 2:
                    part_name_title[-1] += ', '
                elif i1 < len_drops - 1:
                    part_name_title[-1] += ', and '

        stats_all = tmp.stack().reset_index()
        stats_all = stats_all.drop(stats_all.columns[0:-1], axis=1).describe().T
        use_log = True if np.abs(np.log10(stats_all['min'][0]) - np.log10(stats_all['max'][0])) > 1 else False
        # figure types: sharp plot, smooth, const plot, ybar, xbar
        use_limits = {'miny': None, 'maxy': None}
        if np.abs(stats_all['max'][0] - stats_all['min'][0]) < np.abs(stats_all['max'][0] / 200):
            if stats_all['min'][0] < 0:
                use_limits['miny'] = round(1.01 * stats_all['min'][0], 6)
            else:
                use_limits['miny'] = round(0.99 * stats_all['min'][0], 6)
            if stats_all['max'][0] < 0:
                use_limits['maxy'] = round(0.99 * stats_all['max'][0], 6)
            else:
                use_limits['maxy'] = round(1.01 * stats_all['max'][0], 6)
        else:
            if stats_all['min'][0] < (stats_all['mean'][0] - stats_all['std'][0] * 2.576):
                use_limits['miny'] = round(stats_all['mean'][0] - stats_all['std'][0] * 2.576, 6)
            if stats_all['max'][0] > (stats_all['mean'][0] + stats_all['std'][0] * 2.576):
                use_limits['maxy'] = round(stats_all['mean'][0] + stats_all['std'][0] * 2.576, 6)
        reltex_name = os.path.join(ret['rel_data_path'], b_mean_name[-1])
        fig_name = 'Mean combined R \\& t errors over\\\\properties ' + part_name_title[-1] + \
                   '\\\\vs ' + replaceCSVLabels(str(dp), True) + \
                   ' for parameter variations of\\\\' + strToLower(ret['sub_title_it_pars'])
        tex_infos['sections'].append({'file': reltex_name,
                                      'name': fig_name.replace('\\\\', ' '),
                                      'title': fig_name,
                                      'title_rows': fig_name.count('\\\\'),
                                      'fig_type': 'smooth',
                                      'plots': data_it_b_columns[-1],
                                      'label_y': 'mean R \\& t error',  # Label of the value axis. For xbar it labels the x-axis
                                      # Label/column name of axis with bars. For xbar it labels the y-axis
                                      'label_x': replaceCSVLabels(str(dp)),
                                      # Column name of axis with bars. For xbar it is the column for the y-axis
                                      'print_x': str(dp),
                                      # Set print_meta to True if values from column plot_meta should be printed next to each bar
                                      'print_meta': False,
                                      'plot_meta': None,
                                      # A value in degrees can be specified to rotate the text (Use only 0, 45, and 90)
                                      'rotate_meta': 0,
                                      'limits': use_limits,
                                      # If None, no legend is used, otherwise use a list
                                      'legend': column_legend[-1],
                                      'legend_cols': None,
                                      'use_marks': ret['use_marks'],
                                      # The x/y-axis values are given as strings if True
                                      'use_string_labels': True if not is_numeric[-1] else False,
                                      'use_log_y_axis': use_log,
                                      'large_meta_space_needed': False,
                                      'caption': fig_name.replace('\\\\', ' ')
                                      })
        tex_infos['sections'][-1]['legend_cols'] = calcNrLegendCols(tex_infos['sections'][-1])

    template = ji_env.get_template('usac-testing_2D_bar_chart_and_meta.tex')
    rendered_tex = template.render(title=tex_infos['title'],
                                   make_index=tex_infos['make_index'],
                                   ctrl_fig_size=tex_infos['ctrl_fig_size'],
                                   figs_externalize=tex_infos['figs_externalize'],
                                   fill_bar=tex_infos['fill_bar'],
                                   sections=tex_infos['sections'],
                                   abbreviations=tex_infos['abbreviations'])
    t_main_name = 'mean_RTerrors_over_different_properties_vs_1_property'
    base_out_name = 'tex_' + t_main_name
    texf_name = base_out_name + '.tex'
    if ret['build_pdf'][1]:
        pdf_name = base_out_name + '.pdf'
        res = abs(compile_tex(rendered_tex,
                              ret['tex_folder'],
                              texf_name,
                              tex_infos['make_index'],
                              os.path.join(ret['pdf_folder'], pdf_name),
                              tex_infos['figs_externalize']))
    else:
        res = abs(compile_tex(rendered_tex, ret['tex_folder'], texf_name, False))
    if res != 0:
        ret['res'] += res
        warnings.warn('Error occurred during writing/compiling tex file', UserWarning)

    tex_infos = {'title': 'Minimum Mean Combined R \\& t Errors Over Different Properties ' +
                          ' for Parameter Variations of ' + ret['sub_title_it_pars'],
                 'sections': [],
                 # Builds an index with hyperrefs on the beginning of the pdf
                 'make_index': True,
                 # If True, the figures are adapted to the page height if they are too big
                 'ctrl_fig_size': True,
                 # If true, a pdf is generated for every figure and inserted as image in a second run
                 'figs_externalize': False,
                 # If true and a bar chart is chosen, the bars a filled with color and markers are turned off
                 'fill_bar': True,
                 # Builds a list of abbrevations from a list of dicts
                 'abbreviations': ret['gloss']
                 }
    data_parts_min = []
    for df, dp, dit, fn, pnt, isn, dps in zip(b_mean_l,
                                              data_parts,
                                              data_it_indices,
                                              b_mean_name,
                                              part_name_title,
                                              is_numeric,
                                              drops):
        tmp = df.reset_index().set_index(ret['it_parameters'])
        if len(ret['it_parameters']) > 1:
            tmp.index = dit
            tmp.index.name = it_pars_name
        tmp.rename(columns={tmp.columns[1]: 'b_min'}, inplace=True)
        tmp.reset_index(inplace=True)
        data_parts_min.append(tmp.loc[tmp.groupby(dp)['b_min'].idxmin()].set_index(dp))
        # data_parts_min[-1]['tex_it_pars'] = insert_opt_lbreak(data_parts_min[-1][it_pars_name].tolist())
        data_parts_min[-1]['tex_it_pars'] = data_parts_min[-1][it_pars_name].apply(lambda x: tex_string_coding_style(x))
        data_f_name = fn.replace('data_mean','data_min_mean')
        fb_mean_name = os.path.join(ret['tdata_folder'], data_f_name)
        with open(fb_mean_name, 'a') as f:
            f.write('# Minimum mean combined R & t errors (b_min) and their corresponding options over properties ' +
                    '-'.join(map(str, dps)) +
                    ' compared to ' + str(dp) + ' for options ' +
                    '-'.join(ret['it_parameters']) + '\n')
            data_parts_min[-1].to_csv(index=True, sep=';', path_or_buf=f, header=True, na_rep='nan')

        stats_all = data_parts_min[-1].drop([it_pars_name, 'tex_it_pars'], axis=1).stack().reset_index()
        stats_all = stats_all.drop(stats_all.columns[0:-1], axis=1).describe().T
        use_log = True if np.abs(np.log10(stats_all['min'][0]) - np.log10(stats_all['max'][0])) > 1 else False
        # figure types: sharp plot, smooth, const plot, ybar, xbar
        use_limits = {'miny': None, 'maxy': None}
        if np.abs(stats_all['max'][0] - stats_all['min'][0]) < np.abs(stats_all['max'][0] / 200):
            if stats_all['min'][0] < 0:
                use_limits['miny'] = round(1.01 * stats_all['min'][0], 6)
            else:
                use_limits['miny'] = round(0.99 * stats_all['min'][0], 6)
            if stats_all['max'][0] < 0:
                use_limits['maxy'] = round(0.99 * stats_all['max'][0], 6)
            else:
                use_limits['maxy'] = round(1.01 * stats_all['max'][0], 6)
        reltex_name = os.path.join(ret['rel_data_path'], data_f_name)
        fig_name = 'Minimum mean combined R \\& t errors and their corresponding parameter over\\\\properties ' + \
                   pnt + '\\\\vs ' + replaceCSVLabels(str(dp), True) + \
                   ' for parameter variations of\\\\' + strToLower(ret['sub_title_it_pars'])
        caption = 'Minimum mean combined R \\& t errors ' \
                  '(corresponding parameter on top of each bar) over properties ' + \
                  pnt + ' vs ' + replaceCSVLabels(str(dp), True) + \
                  ' for parameter variations of ' + strToLower(ret['sub_title_it_pars'])
        tex_infos['sections'].append({'file': reltex_name,
                                      'name': fig_name.replace('\\\\', ' '),
                                      'title': fig_name,
                                      'title_rows': fig_name.count('\\\\'),
                                      'fig_type': 'ybar',
                                      'plots': ['b_min'],
                                      'label_y': 'min. mean R \\& t error',
                                      # Label of the value axis. For xbar it labels the x-axis
                                      # Label/column name of axis with bars. For xbar it labels the y-axis
                                      'label_x': replaceCSVLabels(str(dp)),
                                      # Column name of axis with bars. For xbar it is the column for the y-axis
                                      'print_x': str(dp),
                                      # Set print_meta to True if values from column plot_meta should be printed next to each bar
                                      'print_meta': True,
                                      'plot_meta': ['tex_it_pars'],
                                      # A value in degrees can be specified to rotate the text (Use only 0, 45, and 90)
                                      'rotate_meta': 45,
                                      'limits': use_limits,
                                      # If None, no legend is used, otherwise use a list
                                      'legend': None,
                                      'legend_cols': 1,
                                      'use_marks': False,
                                      # The x/y-axis values are given as strings if True
                                      'use_string_labels': True if not isn else False,
                                      'use_log_y_axis': use_log,
                                      'large_meta_space_needed': True,
                                      'caption': caption
                                      })
    rendered_tex = template.render(title=tex_infos['title'],
                                   make_index=tex_infos['make_index'],
                                   ctrl_fig_size=tex_infos['ctrl_fig_size'],
                                   figs_externalize=tex_infos['figs_externalize'],
                                   fill_bar=tex_infos['fill_bar'],
                                   sections=tex_infos['sections'],
                                   abbreviations=tex_infos['abbreviations'])
    t_main_name = 'min_mean_RTerrors_over_different_properties_vs_1_property'
    base_out_name = 'tex_' + t_main_name
    texf_name = base_out_name + '.tex'
    if ret['build_pdf'][2]:
        pdf_name = base_out_name + '.pdf'
        res = abs(compile_tex(rendered_tex,
                              ret['tex_folder'],
                              texf_name,
                              tex_infos['make_index'],
                              os.path.join(ret['pdf_folder'], pdf_name),
                              tex_infos['figs_externalize']))
    else:
        res = abs(compile_tex(rendered_tex, ret['tex_folder'], texf_name, False))
    if res != 0:
        ret['res'] += res
        warnings.warn('Error occurred during writing/compiling tex file', UserWarning)

    data_min = pd.concat(data_parts_min, ignore_index=True)#, sort=False, copy=False)
    data_min_c = data_min[it_pars_name].value_counts()
    if data_min_c.count() > 1:
        if data_min_c.iloc[0] == data_min_c.iloc[1]:
            data_min_c = data_min_c.loc[data_min_c == data_min_c.iloc[0]]
            data_min2 = data_min.loc[data_min[it_pars_name].isin(data_min_c.index.values)]
            data_min2 = data_min2.loc[data_min2['b_min'].idxmin()]
            th_mean = float(data_min2[ret['grp_names'][-2]])
            alg = str(data_min2[ret['b'].columns.name])
            b_min = float(data_min2['b_min'])
        else:
            data_min2 = data_min.loc[data_min[it_pars_name] == data_min_c.index.values[0]]
            if len(data_min2.shape) == 1:
                alg = str(data_min2[it_pars_name])
                b_min = float(data_min2['b_min'])
            else:
                alg = str(data_min2[it_pars_name].iloc[0])
                b_min = float(data_min2['b_min'].mean())
    else:
        alg = str(data_min[it_pars_name].iloc[0])
        b_min = float(data_min['b_min'].mean())

    main_parameter_name = keywords['res_par_name']
    # Check if file and parameters exist
    from usac_eval import check_par_file_exists, NoAliasDumper
    ppar_file, ret['res'] = check_par_file_exists(main_parameter_name, ret['res_folder'], ret['res'])

    with open(ppar_file, 'a') as fo:
        # Write parameters
        alg_comb_bestl = alg.split('-')
        if len(keywords['it_parameters']) != len(alg_comb_bestl):
            raise ValueError('Nr of refine algorithms does not match')
        alg_w = {}
        for i, val in enumerate(keywords['it_parameters']):
            alg_w[val] = alg_comb_bestl[i]
        yaml.dump({main_parameter_name: {'Algorithms': alg_w,
                                         'b_min': b_min}},
                  stream=fo, Dumper=NoAliasDumper, default_flow_style=False)

    return ret['res']


def estimate_alg_time_fixed_kp_agg(**vars):
    if 'res_par_name' not in vars:
        raise ValueError('Missing parameter res_par_name')
    tmp, col_name = get_time_fixed_kp(**vars)

    tmp.set_index(vars['it_parameters'], inplace=True)
    from statistics_and_plot import glossary_from_list
    if len(vars['it_parameters']) > 1:
        gloss = glossary_from_list([str(b) for a in tmp.index for b in a])
        par_cols = ['-'.join(map(str, a)) for a in tmp.index]
        tmp.index = par_cols
        it_pars_cols_name = '-'.join(map(str, vars['it_parameters']))
        tmp.index.name = it_pars_cols_name
    else:
        gloss = glossary_from_list([str(a) for a in tmp.index])
        it_pars_cols_name = vars['it_parameters'][0]
        par_cols = [a for a in tmp.index]
    tmp['pars_tex'] = insert_opt_lbreak(par_cols)

    tmp_min = tmp.loc[[tmp[col_name].idxmin(axis=0)]].reset_index()

    vars = prepare_io(**vars)
    from statistics_and_plot import tex_string_coding_style, compile_tex, calcNrLegendCols, replaceCSVLabels, strToLower
    t_main_name = 'mean_time_for_' + \
                  str(int(vars['nr_target_kps'])) + 'kpts_for_opts_' + \
                  '-'.join(map(str, vars['it_parameters']))
    t_mean_name = 'data_' + t_main_name + '.csv'
    ft_mean_name = os.path.join(vars['tdata_folder'], t_mean_name)
    with open(ft_mean_name, 'a') as f:
        f.write('# Mean execution times extrapolated for ' +
                str(int(vars['nr_target_kps'])) + ' keypoints' + '\n')
        f.write('# Row (column options) parameters: ' + '-'.join(vars['it_parameters']) + '\n')
        tmp.to_csv(index=True, sep=';', path_or_buf=f, header=True, na_rep='nan')

    title = 'Mean Execution Times for Parameter Variations of ' + vars['sub_title_it_pars'] + \
            ' Extrapolated for ' + str(int(vars['nr_target_kps'])) + ' Keypoints'
    tex_infos = {'title': title,
                 'sections': [],
                 # Builds an index with hyperrefs on the beginning of the pdf
                 'make_index': False,
                 # If True, the figures are adapted to the page height if they are too big
                 'ctrl_fig_size': False,
                 # If true, a pdf is generated for every figure and inserted as image in a second run
                 'figs_externalize': False,
                 # If true and a bar chart is chosen, the bars a filled with color and markers are turned off
                 'fill_bar': True,
                 # Builds a list of abbrevations from a list of dicts
                 'abbreviations': gloss
                 }
    min_val = tmp[col_name].min()
    max_val = tmp[col_name].max()
    stats_all = {'min': min_val, 'max': max_val}
    use_log = True if np.abs(np.log10(min_val) - np.log10(max_val)) > 1 else False
    # figure types: sharp plot, smooth, const plot, ybar, xbar
    use_limits = {'miny': None, 'maxy': None}
    if np.abs(stats_all['max'] - stats_all['min']) < np.abs(stats_all['max'] / 200):
        if stats_all['min'] < 0:
            use_limits['miny'] = round(1.01 * stats_all['min'], 6)
        else:
            use_limits['miny'] = round(0.99 * stats_all['min'], 6)
        if stats_all['max'] < 0:
            use_limits['maxy'] = round(0.99 * stats_all['max'], 6)
        else:
            use_limits['maxy'] = round(1.01 * stats_all['max'], 6)
    reltex_name = os.path.join(vars['rel_data_path'], t_mean_name)
    fig_name = 'Mean execution times for parameter variations of\\\\' + strToLower(vars['sub_title_it_pars']) + \
               '\\\\extrapolated for ' + str(int(vars['nr_target_kps'])) + ' keypoints'
    tex_infos['sections'].append({'file': reltex_name,
                                  'name': fig_name.replace('\\\\', ' '),
                                  'title': fig_name,
                                  'title_rows': fig_name.count('\\\\'),
                                  'fig_type': 'ybar',
                                  'plots': [col_name],
                                  'label_y': 'mean execution time/$\\mu s$',
                                  # Label of the value axis. For xbar it labels the x-axis
                                  # Label/column name of axis with bars. For xbar it labels the y-axis
                                  'label_x': 'Parameter',
                                  # Column name of axis with bars. For xbar it is the column for the y-axis
                                  'print_x': 'pars_tex',
                                  # Set print_meta to True if values from column plot_meta should be printed next to each bar
                                  'print_meta': False,
                                  'plot_meta': None,
                                  # A value in degrees can be specified to rotate the text (Use only 0, 45, and 90)
                                  'rotate_meta': 0,
                                  'limits': use_limits,
                                  # If None, no legend is used, otherwise use a list
                                  'legend': None,
                                  'legend_cols': 1,
                                  'use_marks': False,
                                  # The x/y-axis values are given as strings if True
                                  'use_string_labels': True,
                                  'use_log_y_axis': use_log,
                                  'large_meta_space_needed': False,
                                  'caption': fig_name.replace('\\\\', ' ')
                                  })
    template = ji_env.get_template('usac-testing_2D_bar_chart_and_meta.tex')
    rendered_tex = template.render(title=tex_infos['title'],
                                   make_index=tex_infos['make_index'],
                                   ctrl_fig_size=tex_infos['ctrl_fig_size'],
                                   figs_externalize=tex_infos['figs_externalize'],
                                   fill_bar=tex_infos['fill_bar'],
                                   sections=tex_infos['sections'],
                                   abbreviations=tex_infos['abbreviations'])
    base_out_name = 'tex_' + t_main_name
    texf_name = base_out_name + '.tex'
    if any(vars['build_pdf']):
        pdf_name = base_out_name + '.pdf'
        res = abs(compile_tex(rendered_tex,
                              vars['tex_folder'],
                              texf_name,
                              False,
                              os.path.join(vars['pdf_folder'], pdf_name),
                              tex_infos['figs_externalize']))
    else:
        res = abs(compile_tex(rendered_tex, vars['tex_folder'], texf_name, False))
    if res != 0:
        warnings.warn('Error occurred during writing/compiling tex file', UserWarning)

    main_parameter_name = vars['res_par_name']#'USAC_opt_refine_min_time'
    # Check if file and parameters exist
    from usac_eval import check_par_file_exists, NoAliasDumper
    ppar_file, res = check_par_file_exists(main_parameter_name, vars['res_folder'], res)

    with open(ppar_file, 'a') as fo:
        # Write parameters
        alg_comb_bestl = tmp_min[it_pars_cols_name][0].split('-')
        min_t = float(tmp_min[col_name][0])
        if len(vars['it_parameters']) != len(alg_comb_bestl):
            raise ValueError('Nr of refine algorithms does not match')
        alg_w = {}
        for i, val in enumerate(vars['it_parameters']):
            alg_w[val] = alg_comb_bestl[i]
        yaml.dump({main_parameter_name: {'Algorithms': alg_w,
                                         't_min': min_t}},
                  stream=fo, Dumper=NoAliasDumper, default_flow_style=False)

    return res
