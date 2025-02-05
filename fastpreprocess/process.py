from fastpreprocess.operation import *

ALL = 'ALL###'
Drop = "drop"
SetColumn_numeric = "set_numeric"
SetColumn_categorical = "set_categorical"
SetColumn_date = 'date_makeit'
Dtype_int = 'dtype_integer'
Dtype_float = 'dtype_float'
FillMissing_mode = 'fillmissing_mode'
FillMissing_median = 'fillmissing_median'
FillMissing_mean = 'fillmissing_mean'
FillMissing_0 = 'fillmissing_0'
GetDummy = 'get_dummy'
LabelEncode = 'label_encode'
AddDatepart = 'date_addit'
StandardScaler = 'scalar_standard'
MinMaxScaler = 'scalar_minmax'


def load_obj(filename = 'fp_pickle.pkl'):
    import pickle
    with open(filename, 'rb') as file:
        df = pickle.load(file)
    return df

class PreProcess:
    
    def __init__(self, copy) -> None:
        self.copy = copy
        self.params = []
        self.log = []

    def replace(self, rep, column, to, reg):
        try:
            self.copy[column] = self.copy[column].replace(to_replace = rep, value = to, regex=reg)
            self.log.append(f"Performed replace for column: {column}")
            return f"Replaced Value {to}"
        except Exception as e:
            self.log.append(f"Performed replace for column: {column} is FAILED, due to {e}")
            return f"Failed to replace value {to}"

    def get_dummy_(self, column):
        try:
            self.copy = pd.get_dummies(self.copy, columns=[column])
            self.log.append(f"Performed get_dummy_ for column: {column}")
            return f"get dummy for {column} is done."
        except Exception as e:
            error = f"Performed get_dummy_ for column: {column} is FAILED, due to {e}"
            self.log.append(error)
            return error

    def drop_column_(self, column):
        try:
            self.copy = self.copy.drop(column, axis=1)
            self.log.append(f"Performed drop_column for column: {column}")
            return f"drop column {column} is done"
        except Exception as e:
            error = f"Performed drop_column_ for column: {column} is FAILED, due to {e}"
            self.log.append(error)
            return error

    def missing_(self, column, method):
        self.log.append(f"Performed fill_missing for column: {column}, method: {method}")
        if method == 'median':
            self.copy[column] = self.copy[column].fillna(self.copy[column].median())
            return f"Filled Missing value with {method}"
        elif method == 'mean':
            self.copy[column] = self.copy[column].fillna(self.copy[column].mean())
            return f"Filled Missing value with {method}"
        elif method == '0':
            self.copy[column] = self.copy[column].fillna(0)
            return f"Filled Missing value with {method}"
        else:
            self.copy[column] = self.copy[column].fillna(self.copy[column].mode()[0])
            return f"Filled Missing value with {method}"


    def convert_(self, column, method, downcast="float"):
        self.log.append(f"Performed type_conversion for column: {column}, ToType: {method}")
        if method == "categorical":
            self.copy[column] = self.copy[column].astype("category")
            return f"Converted column {column} astype to category"
        
        if method == "dtype":
            self.copy[column].astype()
        else:
            self.copy[column] = pd.to_numeric(self.copy[column], errors='coerce', downcast=downcast)
            return f"Converted column {column} to_numeric({downcast}). Note: we handled errors = 'coerce'. So, we're requested to perform 'Fillmissing' Action."



    def label_encode_(self, column):
        self.log.append(f"Performed label_encoding for column: {column}")
        self.convert_(column, 'categorical')
        d = dict(enumerate(self.copy[column].cat.categories))
        self.copy[column] = self.copy[column].cat.codes
        self.params.append({'EncodeType': 'LabelEncode', 'column': column, 'values': d})
        return f"Label Encoded: {d}"



    def scaler_(self, column, method):
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
        if method == 'standard':
            try:
                scalar = StandardScaler()
                values = scalar.fit_transform(self.copy[column].values.reshape(-1, 1))
                self.copy[column] = pd.Series(np.squeeze(values, 1))
                params_ = {'Scaler': 'StandardScaler','column': column, 'mean': scalar.mean_[0], 'scale': scalar.scale_[0], 'variance': scalar.var_[0]}
                self.params.append(params_)
                self.log.append(f"Performed Scaling for column: {column}, Scalar: StandardScaler")
                return f"{column} Standardized: {params_}"
            except Exception as e:
                self.log.append(f"Performed Scaling for column: {column}, Scalar: StandardScaler is Failed, due to {e}")
                return f"Error When Standardize {column}: {e}"
    
        else:
            try:
                scalar = MinMaxScaler()
                values = scalar.fit_transform(self.copy[column].values.reshape(-1, 1))
                self.copy[column] = pd.Series(np.squeeze(values, 1))
                params_ = {'Scaler': 'MinMaxScaler','column': column, 'data_min': scalar.data_min_[0], 'data_max': scalar.data_max_[0], 'data_range': scalar.data_range_[0]}
                self.params.append(params_)
                self.log.append(f"Performed Scaling for column: {column}, Scalar: MinMaxScaler")
                return f"{column} MinMaxScaling Finished: {params_}"
            except Exception as e:
                self.log.append(f"Performed Scaling for column: {column}, Scalar: MinMaxScaler is Failed, due to {e}")
                return f"Error When Min Max scaling {column}: {e}"


class FastPreProcess(PreProcess):

    def __init__(self, file: TypeVar('pandas.core.frame.DataFrame'), analyse = True, Notebook = True) -> None:
        self.copy = file
        self.col = self.copy.columns
        self.Notebook = Notebook
        self.process = IndividualVariable(self.copy)
        if analyse:
            self.process.start()
        
        super().__init__(self.copy)

    def _make_date(self, date_field):
        "Make sure `df[date_field]` is of the right date type." # Fastai Function
        field_dtype = self.copy[date_field].dtype
        try:
            if isinstance(field_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
                field_dtype = np.datetime64
            if not np.issubdtype(field_dtype, np.datetime64):
                self.copy[date_field] = pd.to_datetime(self.copy[date_field], infer_datetime_format=True)
            msg = f"Performed SetColumnDateTime for column {date_field} is done."
            self.log.append(msg)
            if self.Notebook: print('SetColumn_date done 👍')
            else: return msg
        except Exception as e:
            msg = f"Performed SetColumnDateTime for column {date_field} is Failed due to {e}"
            self.log.append(msg)
            return msg

    def _add_datepart(self, field_name, prefix=None, drop=True, time=False):
        "Helper function that adds columns relevant to a date in the column `field_name` of `df`." # Fastai Function
        try:
            self._make_date(field_name)
            field = self.copy[field_name]
            prefix = ifnone(prefix, re.sub('[Dd]ate$', '', field_name))
            attr = ['Year', 'Month', 'Week', 'Day', 'Dayofweek', 'Dayofyear', 'Is_month_end', 'Is_month_start',
                'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']
            if time: attr = attr + ['Hour', 'Minute', 'Second']
            # Pandas removed `dt.week` in v1.1.10
            week = field.dt.isocalendar().week.astype(field.dt.day.dtype) if hasattr(field.dt, 'isocalendar') else field.dt.week
            for n in attr: self.copy[prefix + n] = getattr(field.dt, n.lower()) if n != 'Week' else week
            mask = ~field.isna()
            self.copy[prefix + 'Elapsed'] = np.where(mask,field.values.astype(np.int64) // 10 ** 9,np.nan)
            if drop: self.copy.drop(field_name, axis=1, inplace=True)
            msg = f"Performed AddDatePart for column {field_name} is done."
            self.log.append(msg)
            if self.Notebook: print('AddDatePart Done 👍\n')
            else: return msg
        except Exception as e:
            msg = f"Performed AddDatePart for column {field_name} is Failed due to {e}"
            self.log.append(msg)
            if self.Notebook: 
                print('AddDatePart Failed 🤔\n')
                print(e)
            else: return msg
    
    def _add_date(self, action, column):
        if action == "addit": return self._add_datepart(column)
        else: return self._make_date(column)

    def sample(self, num = 5) -> SampleData:
        if self.Notebook:
            print(f"Sample {num}\n")
            print(self.copy.sample(num).to_string())
            print('\n')
        else:
            return SampleData(num, self.copy.sample(num).values.tolist(), self.copy.columns,
                          len(self.copy.columns), len(self.copy))
             
    def quick_stat(self) -> QuickStat:
        obj = self.copy
        
        try:
            stat = obj.describe().round(3)
            numerical_col = stat.columns
            zipping = [(variable, data) for variable, data in zip(QuickStat().variables, stat.values)]
            if self.Notebook: print(stat.to_string())
            else: return QuickStat(stat, numerical_col, zipping)
        except:
            return 0

    def correlation(self) -> Correlation:
        
        # -------------------------------------------Debuging----------------------------------------
        corr = self.copy.corr()
        if self.Notebook:
            print(corr.to_string())
        else: 
            if len(corr) > 1:
                index = [k for i, k in zip(~corr.iloc[:1].isna().values.flatten(), corr.columns.values) if i]
                corr = corr[index].dropna()
                corr = np.round(corr.values, 3).tolist()
                return Correlation(variable = index, correlation = corr, empty=1) if len(index) > 1 \
                   else Correlation(variable = None, correlation = None, empty=0)
        # -------------------------------------------Debuging----------------------------------------
        
            return Correlation(variable = None, correlation = None, empty=0)

    def get_info(self, column):
        temp = self.copy[column]
        if self.Notebook:
            print('Column: ', column)
            print('Dtype: ', temp.dtype)
            print('Count: ', temp.count())
            print('Total Unique value: ', temp.nunique())
            print('Unique Values:\n', temp.unique())
        
        else:
            return {'dtype': f'{temp.dtype}', 'count': str(temp.count()),
                'unique': str(temp.nunique()),
                'unique_values': set(temp.unique().astype(str))}

    def get_head_tail(self, num = 5, show_sample_too = True):
        if self.Notebook:
            if show_sample_too:
                self.sample(num)
            print(f"Head {num}\n")
            print(self.copy.head(num).to_string())
            print('\n')
            print(f"Tail {num}\n")
            print(self.copy.tail(num).to_string())
        else:    
            return self.copy.head(5).values.tolist(), self.copy.tail(5).values.tolist()

    def get_new(self, analyse = True):
        # self.obj = self.copy
        self.process = IndividualVariable(self.copy)
        if analyse:
            self.process.start()

    def dropna(self, analyse = True):
        self.copy = self.copy.dropna()
        self.get_new(analyse)
        self.log.append("Performed dropna for ALL Columns")
        if self.Notebook: print("dropna done 👍")

    def save_params(self):
        import json
        with open('params.json', 'w', encoding='utf-8') as f:
            json.dump(self.params, f, ensure_ascii=False, indent=4)
        if self.Notebook: print("Saved Params to current directory 😊")

    def process_it(self, column: List, action: List, res: bool = False):
        def do_it(act, i):
            if act == 'drop': finished.append(self.drop_column_(i))
            elif act == 'get_dummy': finished.append(self.get_dummy_(i))
            elif act[:11] == 'fillmissing': finished.append(self.missing_(i, act[12:]))
            elif act in ['set_numeric', 'set_categorical']: finished.append(self.convert_(i, act[4:]))
            elif act[:5] == "dtype" : finished.append(self.convert_(i, "dtype", downcast=act[6:]))
            elif act == 'label_encode': finished.append(self.label_encode_(i)) 
            elif act[:6] == 'scalar': finished.append(self.scaler_(i, act[7:]))
            elif act[:4] == 'date': finished.append(self._add_date(action=act[5:], column=i))
            else: finished.append("cool")

        finished = []

        if "ALL###" in column:
            if len(column) == 1: column = self.copy.columns
            elif (column.index("ALL###") == 0) and (len(column) > 1):
                column = [i for i in self.copy.columns if i not in column[1:]]
            else: return "Can't Process!"
        print(column, action)
        for act in tqdm.tqdm(action):
            for i in column: do_it(act, i)

        if not self.Notebook: return str(finished)
