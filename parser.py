from typing import List, Tuple
import numpy as np

# создаём массив данных из schedule файла
def parse_schedule(text: str, keywords_tuple: Tuple[str]) -> List[List[str]]:
    """
    return list of elements ready to be transformed to the resulting DataFrame
    @param text: cleaned input text from .inc file
    @param keywords_tuple: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @return: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...] ready to be transformed
    to the resulting DataFrame
    """
    results = []
    date = None
    indicator = False
    for line in text.splitlines():
        if line in keywords_tuple:
            indicator = True
            keyword = line
            continue
        elif line == '/':
            indicator = False
      
        if indicator:
            if keyword != 'DATES':
                res = [np.nan if date is None else date]
                res.extend(parse_keyword_COMPDAT_line(line))
            else:
                date = parse_keyword_DATE_line(line)
                res = [date, np.nan]
            results.append(res) 
            
    filter_results = []
    for i in range(len(results)-1):
        if not isinstance(results[i][0], str):
            filter_results.append(results[i])
        elif i == len(results):
            filter_results.append(results[i])
        else:
            if results[i][0] == results[i+1][0] and len(results[i]) > 2:
                filter_results.append(results[i])
            elif results[i][0] != results[i+1][0]:
                filter_results.append(results[i])   
    filter_results.append(results[-1])
    
    return filter_results
    
# убираем разделитель
def parse_keyword_DATE_line(current_date_line: str) -> str:
    """
    parse a line related to a current DATA keyword block
    @param current_date_line: line related to a current DATA keyword block
    @return: list of parameters in a DATE line
    """
    return current_date_line.replace(' /', '').replace('/', '')

# формирование списка соответствующих значений строчек с данными по перфорации
def parse_keyword_COMPDAT_line(well_comp_line: str) -> List[str]:
    """
    parse a line related to a current COMPDAT keyword block
    @param well_comp_line: line related to a current COMPDAT keyword block
    @return: list of parameters (+ NaN Loc. grid. parameter) in a COMPDAT line
    """
    result = well_comp_line.replace(' /', '').replace('/', '').split()
    try:
        if isinstance(float(result[1]), float):
            result.insert(1, np.nan)
    except:
        pass
    for index, element in enumerate(result):
        if not isinstance(element, float):
            if element.find('*') != -1:
                
                n = int(element[0])
                
                result.remove(result[index])
                for _ in range(n):
                    result.insert(index, 'DEFAULT')
            else:
                result[index] = element.replace("'","")
  
    return result

# аналогичные дествия совершаем для compdatl
def parse_keyword_COMPDATL_line(well_comp_line: str) -> List[str]:
    """
    parse a line related to a current COMPDATL keyword block
    @param well_comp_line: line related to a current COMPDATL keyword block
    @return: list of parameters in a COMPDATL line
    """
    return parse_keyword_COMPDAT_line(well_comp_line)
    
# заменяем дефолтные значения в строке
def default_params_unpacking_in_line(line: str) -> str:
    """
    unpack default parameters set by the 'n*' expression
    @param line: line related to a current COMPDAT/COMPDATL keyword block
    @return: the unpacked line related to a current COMPDAT/COMPDATL keyword block
    """
    while line.find('*') != -1:
        n = line[line.find('*')-1]
        s = ''
        for _ in range(int(n)):
            s += 'DEFAULT' if s == '' else ' DEFAULT' 
           
        line = line.replace(f'{n}*', s)
    return line
    