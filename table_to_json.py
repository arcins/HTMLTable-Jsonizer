import json
import numpy as np

from bs4 import BeautifulSoup


class TableToJSON:
    '''
    Converts table from html document to json format
    '''

    def __init__(self, file_name):
        with open(file_name) as fp:
            soup = BeautifulSoup(fp.read(), "lxml")
        self.converted_tr = soup.find_all('tr')
        self.table_width = 0

        # find width of the table
        for single_td in self.converted_tr[0].find_all('th'):
            self.table_width += int(single_td.get("colspan", "1"))

        # add only td to table named temporary_table_td
        self.temporary_table_td = TableToJSON.create_matrix(self, 'td')

        # add only th to table named temporary_table_th
        self.temporary_table_th = TableToJSON.create_matrix(self, 'th')


    #return matrix maked from table for specified tag.
    def create_matrix(self, tag_type):
        temporary_table = np.empty(shape=(len(self.converted_tr), self.table_width), dtype=object)
        for idx, single_tr in enumerate(self.converted_tr):
            column_shift = 0  # when encouter colspan add number
            for idxtd, single_td in enumerate(single_tr.find_all(lambda tag: tag.name == 'td' or tag.name == 'th')):
                if single_td.name == tag_type:
                    while temporary_table[idx, idxtd + column_shift] is not None:
                        column_shift += 1

                    colspan_range = int(single_td.get("colspan", "1"))
                    rowspan_range = int(single_td.get("rowspan", "1"))

                    if colspan_range == 1 and rowspan_range == 1:
                        temporary_table[idx, idxtd + column_shift] = single_td.text.strip()
                    else:
                        for j in range(rowspan_range):
                            for i in range(colspan_range):
                                while temporary_table[idx + j, idxtd + column_shift + i]:
                                    column_shift += 1
                                temporary_table[idx + j, idxtd + column_shift + i] = single_td.text.strip()
                        column_shift += int(colspan_range) - 1
        return temporary_table


    # search for th in each matrix row to the left from td (is_row) or in each column above td
    def __search_th(self, search_range, pos_td, is_row):
        temp_name = ''

        for s in range(search_range):
            if is_row:
                second_pos, first_pos = s, pos_td
            else:
                second_pos, first_pos = pos_td, s

            if self.temporary_table_th[first_pos,  second_pos]:
                temp_name = temp_name + self.temporary_table_th[first_pos,  second_pos] + '.'

        return temp_name


    def show_td_matrix(self):
        print('Matrix for <td>: \n', self.temporary_table_td)


    def show_th_matrix(self):
        print('\nMatrix for <th>: \n', self.temporary_table_th)


    def get_json(self):
        #return json format
        temporary_dict = {}

        # change td matrix to dictionary with key from th rows.columns
        for i in range(len(self.converted_tr)):
            for j in range(self.table_width):
                if self.temporary_table_td[i, j]:
                    temporary_dict[(TableToJSON.__search_th(self, j, i, True) + TableToJSON.__search_th(self, i, j, False))[:-1]] = self.temporary_table_td[i, j]

        jsonarray = json.dumps(temporary_dict, ensure_ascii=False)

        return jsonarray


if __name__ == "__main__":
    print(TableToJSON.__doc__)
    vivo = TableToJSON("vivo_ok.html")
    vivo.show_td_matrix()
    vivo.show_th_matrix()
    print('\noutput json:')
    print(vivo.get_json())

