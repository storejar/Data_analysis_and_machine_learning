df_m = np.asmatrix(df)
print(df_m.shape)
delete_rows = []
for row in range(df_m.shape[0]):
    #print(df_m[row,0])
    if int(df_m[row,0]) == 0:
        if int(df_m[row,1]) != 0:
            delete_rows.append(row)
            first = True 
    if int(df_m[row,2]) == 0:
        if int(df_m[row,3]) != 0:
            first = True 
            if row in delete_rows:
                first = False
            if first == True:
                delete_rows.append(row)
    if int(df_m[row,4]) == 0:
        if int(df_m[row,5]) != 0:
            first = True 
            if row in delete_rows:
                first = False
            if first == True:
                delete_rows.append(row)
    if int(df_m[row,1]) < 0:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
    if int(df_m[row,3]) < 0:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
    if int(df_m[row,5]) == -1:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
a=df.iloc[delete_rows, :]
list_df=a.index
df = df.drop(list_df)
