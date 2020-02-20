#!/usr/bin/env python3

from dialog import Dialog
import locale
import json

locale.setlocale(locale.LC_ALL, '')

dwindow = Dialog(dialog='dialog', autowidgetsize=True)
row_count, col_count = dwindow.maxsize()
wrap_len = col_count - 30

dwindow.set_background_title('MadLib')

#   open files
# load spec file
fieldspec = {}
with open('fields.json') as f:
    fieldspec = json.load(f)

if 'default_exclude' in fieldspec:
    exclude_defaults = fieldspec['default_exclude']

template_lines = []
with open('cl_template.txt') as f:
    template_lines = [(str(i), line.replace('\n', ''))
                      for i, line in enumerate(f.readlines())]

#   select lines for each paragraph
paragraphs = []
first_line = 0
for idx, line in template_lines:
    if not line.strip():
        paragraphs.append(template_lines[first_line:int(idx)])
        first_line = int(idx) + 1

excluded_lines = []
for i, p in enumerate(paragraphs):
    line_choices = [(idx, line, True)
                    if idx in exclude_defaults else (idx, line, False)
                    for idx, line in p]
    for idx, entry in enumerate(line_choices):
        ltag, line, lbool = entry
        if len(line) > wrap_len:
            display_line = line
            l_break = line[:wrap_len].rfind(' ')
            display_line = display_line[:l_break] + '[...]'
            line_choices[idx] = (ltag, display_line, lbool, line)
        else:
            line_choices[idx] = (*entry, line)
    code, t_list = dwindow.checklist(title='Paragraph ' + str(i),
                                     text='Select which lines to exclude',
                                     choices=line_choices,
                                     cr_wrap=True, item_help=True,
                                     help_button=True, 
                                     help_label='See Full Line',
                                     help_status=True)
    while code == Dialog.HELP:
        dwindow.msgbox(t_list[0])
        code, t_list = dwindow.checklist(title='Paragraph ' + str(i),
                                     text='Select which lines to exclude',
                                     choices=t_list[2],
                                     cr_wrap=True, item_help=True,
                                     help_button=True,
                                     help_label='See Full Line',
                                     help_status=True)
    excluded_lines.extend(t_list)

#   option to resave lines to exclude
if dwindow.yesno(str(excluded_lines), title="Excluded Lines",
                 yes_label="Continue", no_label="Save as Default") != Dialog.OK:
    fieldspec['default_exclude'] = excluded_lines
    with open('fields.json', 'w') as f:
        json.dump(fieldspec, f, indent=4, separators=(',', ': '))

#   exclude selected lines from template
included_lines = [line[1] for line in template_lines
                  if line[0] not in excluded_lines]

#   find a line of context for each entry point
fields = fieldspec.get('fields', [])
entries = {i: {} for i in range(len(fields))}
for i in entries:
    for idx, line in enumerate(included_lines):
        #dwindow.msgbox(str(line))
        fill = '{' + str(i) + '}'
        if fill in line:
            entries[i]['context'] = ((included_lines[idx-1] if idx != 0 else '')
                                     + ' \Z5' + line.replace(fill, '\Zb<'
                                                    + fields[i]['title']
                                                    + '>\ZB')
                                     + '\Zn')
            break

#fill entry points
new_field_vals = {}
for idx, field in enumerate(fields):
    for line in included_lines:
        if '{' + str(idx) + '}' in line:
            break
    #field isn't present in the document
    else:
        entries[idx]['value'] = 'n/a'
        continue

    if 'options' in field:
        opts = field['options'] + ['<add new>']
        idxs = [str(i) for i in range(len(opts))]
        ret, choice = dwindow.menu(title=field['title'],
                                   text=entries[idx]['context'],
                                   colors=True,
                                   choices=zip(idxs, opts))
        #enter custom selection if <add new> was selected
        if choice == str(len(opts) - 1):
            ret, choice = dwindow.inputbox(title=field['title'],
                                           text=entries[idx]['context'],
                                           colors=True,
                                           extra_button=True,
                                           extra_label='Save as Option')
        else:
            choice = opts[int(choice)]
    else:
        ret, choice = dwindow.inputbox(title=field['title'],
                                       text=entries[idx]['context'],
                                       colors=True,
                                       extra_button=True,
                                       extra_label='Save as Option')
    result = '' if '<none>' in choice else choice
    if ret == Dialog.EXTRA:
        new_field_vals[idx] = choice
    entries[idx]['value'] = result

#   save any new field vals if requested
for idx, val in new_field_vals.items():
    if 'options' in fieldspec['fields'][idx]:
        fieldspec['fields'][idx]['options'].append(val)
    else:
        fieldspec['fields'][idx]['options'] = [val]

if new_field_vals:
    if dwindow.yesno(str(new_field_vals), title="Save New Options",
                    yes_label="Continue without Saving",
                    no_label="Save to Default") != Dialog.OK:
        fieldspec['default_exclude'] = excluded_lines
        with open('fields.json', 'w') as f:
            json.dump(fieldspec, f, indent=4, separators=(',', ': '))

#   format output and print
field_vals = [entry['value'] for entry in entries.values()]
#dwindow.msgbox(''.join(included_lines) + str(field_vals))
for idx, line in enumerate(included_lines):
    if not line or line[-1] != '.':
        included_lines[idx] = line + '\n'
    else:
        included_lines[idx] = line + ' '
output = ''.join(included_lines).format(*field_vals)
dwindow.msgbox(output)

print()
print(output)

