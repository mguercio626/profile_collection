from BMM.macrobuilder import BMMMacroBuilder

class GridMacroBuilder(BMMMacroBuilder):
    '''A class for parsing specially constructed spreadsheets and
    generating macros for measuring XAS using the Linkam stage.

    Examples
    --------
    >>> gmb = GridMacroBuilder()
    >>> gmb.spreadsheet('grid.xlsx')
    >>> gmb.write_macro()

    '''
        
    def _write_macro(self):
        '''Write a macro paragraph for each sample described in the
        spreadsheet.  A paragraph consists of line to move to the
        correct spinner, lines to find or move to the center-aligned
        location in pitch and Y, lines to move to and from the correct
        glancing angle value, a line to change the edge energy (if
        needed), a line to measure the XAFS using the correct set of
        control parameters, and a line to close plot windows after the
        scan.
        '''
        element, edge, focus = (None, None, None)

        for m in self.measurements:

            if m['default'] is True:
                element     = m['element']
                edge        = m['edge']
                continue
            if self.skip_row(m) is True:
                continue

            #######################################
            # default element/edge(/focus) values #
            #######################################
            for k in ('element', 'edge', 'motor1', 'motor2'):
                if m[k] is None:
                    m[k] = self.measurements[0][k]

            ############################
            # sample and slit movement #
            ############################
            if m['position1'] is not None and m['position2'] is not None:
                self.content += self.tab + f'yield from mv({m["motor1"]}, {m["position1"]:.3f}, {m["motor2"]}, {m["position2"]:.3f})\n'
            else:
                if m['position1'] is not None:
                    self.content += self.tab + f'yield from mv({m["motor1"]}, {m["position1"]:.3f})\n'
                if m['position2'] is not None:
                    self.content += self.tab + f'yield from mv({m["motor2"]}, {m["position2"]:.3f})\n'
            if m['detectorx'] is not None:
                self.content += self.tab + f'yield from mv(xafs_det, {m["detectorx"]:.2f})\n'

            
            ##########################
            # change edge, if needed #
            ##########################
            focus = False
            if m['focus'] == 'focused':
                focus = True
            if self.do_first_change is True:
                self.content += self.tab + 'yield from change_edge(\'%s\', edge=\'%s\', focus=%r)\n' % (m['element'], m['edge'], focus)
                self.do_first_change = False
                self.totaltime += 4
                
            elif m['element'] != element or m['edge'] != edge: # focus...
                element = m['element']
                edge    = m['edge']
                self.content += self.tab + 'yield from change_edge(\'%s\', edge=\'%s\', focus=%r)\n' % (m['element'], m['edge'], focus)
                self.totaltime += 4
                
            else:
                if self.verbose:
                    self.content += self.tab + '## staying at %s %s\n' % (m['element'], m['edge'])
                pass

            ######################################
            # measure XAFS, then close all plots #
            ######################################
            command = self.tab + 'yield from xafs(\'%s.ini\'' % self.basename
            for k in m.keys():
                ## skip cells with macro-building parameters that are not INI parameters
                if self.skip_keyword(k):
                    continue
                ## skip element & edge if they are same as default
                elif k in ('element', 'edge'):
                    if m[k] == self.measurements[0][k]:
                        continue
                ## skip cells with only whitespace
                if type(m[k]) is str and len(m[k].strip()) == 0:
                    m[k] = None
                ## if a cell has data, put it in the argument list for xafs()
                if m[k] is not None:
                    if k == 'filename':
                        fname = self.make_filename(m)
                        command += f', filename=\'{fname}\''
                    elif type(m[k]) is int:
                        command += ', %s=%d' % (k, m[k])
                    elif type(m[k]) is float:
                        command += ', %s=%.3f' % (k, m[k])
                    else:
                        command += ', %s=\'%s\'' % (k, m[k])
            command += ')\n'
            self.content += command
            self.content += self.tab + 'close_last_plot()\n\n'

            ########################################
            # approximate time cost of this sample #
            ########################################
            self.estimate_time(m, element, edge)
            

        if self.close_shutters:
            self.content += self.tab + 'if not dryrun:\n'
            self.content += self.tab + '    BMMuser.running_macro = False\n'
            self.content += self.tab + '    BMM_clear_suspenders()\n'
            self.content += self.tab + '    yield from shb.close_plan()\n'


    def get_keywords(self, row, defaultline):
        '''Instructions for parsing spreadsheet columns into keywords.

        arguments
        ---------
        row : contents of a row as read by openpyxl, i.e. ws.rows
        defaultline : True only if this row contains the default
        parameters, i.e. the green row

        This must return a dictionary.  The dictionary keys are the
        keywords related to the column labels from the spreadsheet,
        the values are cell contents, possibly coerced to a specific
        type.

        '''
        this = {'default':     defaultline,
                'measure':     self.truefalse(row[2].value), # filename and visualization
                'filename':    row[3].value,
                'nscans':      row[4].value,
                'start':       row[5].value,
                'mode':        row[6].value,
                'element':     row[7].value,      # energy range
                'edge':        row[8].value,
                'focus':       row[9].value,
                'sample':      self.escape_quotes(row[10].value),     # scan metadata
                'prep':        self.escape_quotes(row[11].value),
                'comment':     self.escape_quotes(row[12].value),
                'bounds':      row[13].value,     # scan parameters
                'steps':       row[14].value,
                'times':       row[15].value,
                'motor1':      row[16].value,     # motor names and positions 
                'position1':   row[17].value,
                'motor2':      row[18].value,
                'position2':   row[19].value,
                'detectorx':   row[20].value,
                'snapshots':   self.truefalse(row[21].value),  # flags
                'htmlpage':    self.truefalse(row[22].value),
                'usbstick':    self.truefalse(row[23].value),
                'bothways':    self.truefalse(row[24].value),
                'channelcut':  self.truefalse(row[25].value),
                'ththth':      self.truefalse(row[26].value),
                'url':         row[27].value,
                'doi':         row[28].value,
                'cif':         row[29].value, }
        return this
