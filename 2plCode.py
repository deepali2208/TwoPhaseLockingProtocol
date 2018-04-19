#Read_Lock equivalent to "Shared Lock"
#Write_Lock equivalent to "Exclusive Lock"


#Transaction table and lock table are maintained for tracking the transactions and lock on the data item.
#Actions taken list stores all the output and at the end writes into the output file
#Output in Output.txt file

transaction_table = {}
lock_table = {}
actions_taken=[]


#Check for deadlock prevention protocol using wait-die rules to determine if the transaction should wait (be blocked) or die (abort)
#The transaction timestamps are used to decide on which action to take

def waitdie(t1,t2,operation,dataitem,line):
    current_lock_row = lock_table[dataitem]
    trans_list = lock_table[dataitem]['transactionid_list']

    transaction_state_abort = "abort"
    transaction_state_blocked = "blocked"
    ts1 = transaction_table[t1]
    ts2= transaction_table[t2]

    timestamp_ts1 = ts1['Timestamp'] #old
    timestamp_ts2 = ts2['Timestamp'] #new

    if ts1 == ts2:
        return "Both Transactions are same"

    if ts2['trans_state'] != transaction_state_blocked or ts2['trans_state'] != transaction_state_abort:
        if timestamp_ts2 < timestamp_ts1:
            ts2['trans_state'] = transaction_state_blocked
            ts2['waiting_operationslist'].append({'operation':operation, 'dataitem':dataitem})
            current_lock_row['waiting_transactionslist'].append(t2)
            waitdie_blocked = "Line Operation " + line + "Action Taken: Transaction gets Blocked," \
                            " and its get added in Waiting Operations list as: "\
                              +str(ts2['waiting_operationslist']) + ", TransactionId: " + str(t2)

            actions_taken.append(waitdie_blocked)
        else:
            waitdie_aborting = "Line Operation " + line + "Action Taken: Aborting Transaction , " \
                                                         "Ignore subsequent operations, " \
                                                         "TransactionId: " + str(t2)
            actions_taken.append(waitdie_aborting)
            end_transaction(t2,transaction_state_abort,line)




#Process of committing and aborting transaction should release (unlock) any items that are currently locked by the transaction one at a time
#below function unlocks all the items
#The process of unlocking an item should check if any transaction(s) are blocked because of waiting for the item.
#If any transactions are waiting, it should remove the first waiting transaction and grant it access to the item
# and resume the transaction.
#All waiting operations of the transaction are processed

def end_transaction(trans,transaction_state,line):
    global transaction_table
    transaction_state_active = "active"
    lock_state_read = "Read_Lock"
    lock_state_write = "Write_Lock"
    transaction_state_abort = "abort"
    transaction_state_committed = "committed"

    current_trans_row = transaction_table[trans]
    current_trans_row['trans_state']=transaction_state
    current_trans_row['chk_growingphase'] = False

    for d_item in current_trans_row['t_dataitem']:
        current_lock_row = lock_table[d_item]
        trans_list = current_lock_row['transactionid_list']
        waiting_lock_translist = current_lock_row['waiting_transactionslist']

        trans_list.remove(trans)

        if len(waiting_lock_translist)== 0:
            continue

        list_transaction1 = waiting_lock_translist.pop(0)
        transaction1 = transaction_table[list_transaction1]
        operation1 = transaction1['waiting_operationslist'].pop(0)

        if operation1['operation'] == "r":
            if current_lock_row['lock_state'] == lock_state_write:
                current_lock_row['lock_state'] = lock_state_read
                current_lock_row['transactionid_list'] = [list_transaction1]
                transaction1['trans_state'] = transaction_state_active
                next_oper_trans = transaction_table[list_transaction1]['waiting_operationslist'][0]
                if next_oper_trans['operation'] == "e":
                    transaction_table[list_transaction1]['waiting_operationslist'].pop(0)
                    end_trans = "e" + str(list_transaction1)+  " Action Taken: Transaction gets committed" \
                                , "Unlock and release dataitems: " \
                                + str(transaction_table[list_transaction1]['t_dataitem'])
                    actions_taken.append(end_trans)
                    end_transaction(list_transaction1,transaction_state_committed,line)

                for t1 in waiting_lock_translist:
                    trans_t1 = transaction_table[t1]
                    t2 = trans_t1['waiting_operationslist'][0]
                    if t2['operation'] == "r":
                        trans_t1['waiting_operationslist'].pop(0)
                        waiting_lock_translist.remove(t1)
                        trans_t1['trans_state'] = transaction_state_active
                        trans_list.append(t1)
                        next_oper_trans = transaction_table[list_transaction1]['waiting_operationslist'][0]

                        if next_oper_trans['operation'] == "e":
                            transaction_table[list_transaction1]['waiting_operationslist'].pop(0)
                            end_trans = "e" + str(list_transaction1) + " Action Taken: Transaction gets committed" \
                                                 ", Unlock and release dataitems: " \
                                        + str(transaction_table[list_transaction1]['t_dataitem'])
                            actions_taken.append(end_trans)

                            end_transaction(list_transaction1, transaction_state_committed, line)


        elif operation1['operation'] == "w":
            if current_lock_row['lock_state'] == lock_state_read:
                if len(trans_list)==0 or ((len(trans_list))==1 and trans_list[0] == list_transaction1 ):
                    current_lock_row['lock_state'] = lock_state_write
                    trans_list=[list_transaction1]
                    transaction1['trans_state'] = transaction_state_active
                    next_oper_trans_w = transaction_table[list_transaction1]['waiting_operationslist'][0]
                    if next_oper_trans_w['operation'] == "e":
                        transaction_table[list_transaction1]['waiting_operationslist'].pop(0)
                        end_trans = "e" + str(list_transaction1) + " Action Taken: Transaction gets committed" \
                                                 ", Unlock and release dataitems: " \
                                    + str(transaction_table[list_transaction1]['t_dataitem'])
                        actions_taken.append(end_trans)

                        end_transaction(list_transaction1, transaction_state_committed, line)

                elif (len(trans_list) > 0):
                    for t1 in trans_list:
                        waitdieresults = waitdie(t1,list_transaction1,operation1['operation'],operation1['dataitem'],line)
                        if waitdieresults == transaction_state_abort:
                            break;

            elif current_lock_row['lock_state'] == lock_state_write:
                trans_list = [list_transaction1]
                transaction1['trans_state'] = transaction_state_active
                end_trans = "Line Operation " + line + "Action Taken: Trasaction releases read lock on dataitem" \
                            +str(current_lock_row['dataitem'])
                actions_taken.append(end_trans)

                next_oper_trans_w = transaction_table[list_transaction1]['waiting_operationslist'][0]
                if next_oper_trans_w['operation'] == "e":
                    end_trans_e = "Line Operation: e"  + str(list_transaction1) \
                                + " Action Taken: Transaction committed" + ", Unlock and release dataitems: " + str(
                        transaction_table[list_transaction1]['t_dataitem'])
                    actions_taken.append(end_trans_e)

                    transaction_table[list_transaction1]['waiting_operationslist'].pop(0)

                    end_transaction(list_transaction1, transaction_state_committed, line)


    current_trans_row['t_dataitem']=[]

#Processing a read operation and the appropriate read lock(X) request is set and the lock table is updated appropriately
def read_operation(line):
    line1 = line.split(" ")
    operation = line[0]
    transaction_id = line1[0][1]
    dataitem = line1[1][1]
    lock_state_read = "Read_Lock"
    current_trans_row = transaction_table[transaction_id]

    # check whether the schedule is in growing phase
    # If the item is already locked by a non-conflicting read lock, the transaction is added to the list of transactions
    #  that hold the read lock on the requested item (in the lock table).
    if current_trans_row['chk_growingphase'] == True:
        if dataitem in lock_table:
            current_locked_row = lock_table[dataitem]
            if current_locked_row['lock_state'] == "Read_Lock":                             #checking for non conflicting read lock
                if transaction_id not in current_locked_row ['transactionid_list']:         # checking whether transaction exists in the transactionlist in the lock table
                    (current_locked_row['transactionid_list']).append(transaction_id)       #If not exists, add to the list
                    current_trans_row['t_dataitem'].append(dataitem)                        #Add the dataitem to the dataitemlist in transaction table
                    transaction_read_RL = "Line Operation " + line + \
                                       "Action Taken: Added 'Read Lock' for the transactions for dataitem: " \
                                          + str(dataitem)+ ", TransactionId: " + str(transaction_id)

                    #Actions_taken list is used to append all the variables that stores the details of all the actions
                    #occuring and is appended to the list
                    actions_taken.append(transaction_read_RL)

        # If the item is already locked by conflicting Write-Lock then the wait die protocol determines whether the
        #transactions are to be blocked or aborted
            elif current_locked_row['lock_state'] == "Write_Lock":
                if len(current_locked_row['transactionid_list'])==0:                    #transactionlist in lock table is blank
                    current_locked_row['transactionid_list'].append(transaction_id)
                    current_locked_row['lock_state'] = lock_state_read
                    current_trans_row['t_dataitem'].append(dataitem)
                    transaction_read_WL = "Line Operation " + line + \
                               "Action Taken: Lock Status updated as 'Read lock' in the lock table , Modified dataitem is: " \
                               + str(dataitem) + ", TransactionId: " + str(transaction_id)

                    actions_taken.append(transaction_read_WL)


                elif transaction_id not in current_locked_row ['transactionid_list']:
                    t1 = current_locked_row['transactionid_list'][0]
                    waitdie(t1,transaction_id,operation,dataitem,line)

        else:
            lock_table[dataitem] = {'lock_state': lock_state_read,
                                    'transactionid_list': [transaction_id],
                                    'waiting_transactionslist': []}
            transaction_table[transaction_id]['t_dataitem'].append(dataitem)
            transaction_read = "Line Operation " + line + \
                               "Action Taken: Add dataitem entry into lock table, Lock Status updated to 'Read Lock'," \
                               " Added dataitem is: " \
                               + str(dataitem) + \
                               ", Added dataitem to transaction table in t_dataitem" \
                               +str(transaction_table[transaction_id]['t_dataitem'])+ ", TransactionId: " \
                               + str(transaction_id)

            actions_taken.append(transaction_read)

#Write operation performs write on the dataitem

def write_operation(line):
    line1 = line.split(" ")
    operation = line[0]
    transaction_id = line1[0][1]
    dataitem = line1[1][1]
    lock_state_write = "Write_Lock"

    current_trans_row = transaction_table[transaction_id]

    #checks for growing phase, if it is True, then upgrades to Write Lock
    if transaction_table[transaction_id]['chk_growingphase'] == True:
        if dataitem in lock_table:
            current_locked_row = lock_table[dataitem]
            trans_list = current_locked_row['transactionid_list']

            # checks for growing phase, if it is True, then upgrades to Write Lock
            if current_locked_row['lock_state'] == "Read_Lock":                 #Non Conflicting Read Lock
                if (len(trans_list)==1 and trans_list[0] == transaction_id):
                    current_locked_row['lock_state'] = "Write_Lock"

                    transaction_write_RL = "Line Operation " + line + \
                                        "Action Taken: Updating 'Read Lock' to 'Write Lock', " \
                                        ", Modified dataitem is: " \
                                        + str(dataitem) + \
                                        ", TransactionId: " + str(transaction_id)

                    actions_taken.append(transaction_write_RL)
                else:
                    transaction_write_RL_waitdie = "Line Operation " + line + \
                                           "Action Taken: Transaction wants to Write datitem but has " \
                                           ", Multiple Transaction with 'Read Lock'. DataItem: " \
                                           + str(dataitem) + \
                                           ", TransactionId: " + str(transaction_id)

                    actions_taken.append(transaction_write_RL_waitdie)
                    # If the item is already locked by a conflicting read lock,
                    # then wait-die protocol determines the state of transaction
                    # It check for all the transactions in the list, even if one aborts then the it breaks the for loop
                    for t1 in trans_list:
                        waitdieresult = waitdie(t1,transaction_id,operation,dataitem,line)
                        if waitdieresult == "abort":
                            break

            # If the item is already locked by a conflicting Write lock, then wait-die protocol determines the state of transaction
            elif current_locked_row['lock_state'] == "Write_Lock":
                if transaction_id not in trans_list:                #In case of Conflicting Write Lock
                    t1 = trans_list[0]
                    waitdie(t1,transaction_id,operation,dataitem,line)
        else:
            lock_table[dataitem] = {'lock_state': lock_state_write,                 #Insert the data item if it does not exists in lock table
                                    'transactionid_list': [transaction_id],
                                    'waiting_transactionslist': []}
            transaction_table[transaction_id]['t_dataitem'].append(dataitem)        #update the transaction table entry
                                                                                    # for dataitemlist as new entry is added in the lock table for that transaction

            transaction_write = "Line Operation " + line + \
                               "Action Taken: Add dataitem entry into lock table, Lock status updated to 'Write Lock', Added dataitem is: " \
                               + str(dataitem) + \
                               ", Added datatiem to transaction table in t_dataitem, TransactionId: " \
                                + str(transaction_id)

            actions_taken.append(transaction_write)

#Following code reads the file and line and as performs operation accordingly

with open("file.txt", "r") as f:
    timestmp = 0
    for line in f:
        operation = line[0]
        if operation == "I":
            actions_taken.append("\n\n\n Output\n" )
            transaction_table={}
            lock_table={}
            timestmp = 0

        elif operation == "b" or operation == "e":
             transaction_id = line[1]
             #  transaction record should be created in the transaction table when a begin transaction operation (b) is processed
             # (the state of this transaction should be active).
             if operation == "b":
                 t_state = "active"
                 chk_phase = True
                 timestmp = timestmp + 1
                 transaction_table[transaction_id] = {'trans_state': t_state,
                                                       'Timestamp':timestmp,
                                                        'waiting_operationslist': [],
                                                        't_dataitem' : [],
                                                       'chk_growingphase': chk_phase}
                 transaction_created_for_begin = "Line Operation " +line+ \
                        "Action Taken: Add transaction to transaction table, Added TransactionId is " \
                                                 + str(transaction_id)
                 actions_taken.append(transaction_created_for_begin)

             # Processing when transaction reaches its end (e) operation successfully, it should be committed or aborted appropriately
             elif operation == "e":
                 if transaction_id in transaction_table:
                     if transaction_table[transaction_id]['trans_state'] == 'blocked':
                         trans_state_blocked = "blocked"
                         transaction_table[transaction_id]['waiting_operationslist'].append({'operation':operation, 'dataitem' : 'N.A.'})

                         transaction_end_blocked = "Line Operation " + line + \
                                "Action Taken: Transaction already blocked, e1 is added to waiting " \
                                "operations list, Waiting Operations list" \
                                + str(transaction_table[transaction_id]['waiting_operationslist']) + \
                                ", TransactionId is " + str(transaction_id)
                         actions_taken.append(transaction_end_blocked)

                     elif transaction_table[transaction_id]['trans_state'] == 'abort':
                         transaction_end_abort = "Line Operation " + line +\
                                "Action Taken: Transaction already aborted, TransactionId state is: " \
                                + str(transaction_table[transaction_id]['trans_state']) + \
                                ", TransactionId is " + str(transaction_id)
                         actions_taken.append(transaction_end_abort)
                     else:
                         trans_state_commit = "committed"
                         transaction_end_commit = "Line Operation " + line + \
                                                  "Action Taken: End transaction, status updated to " \
                                                  + str(trans_state_commit) + \
                                                  ", TransactionId is " + str(transaction_id) + ", Unlock and release dataitems: " \
                                                  + str(transaction_table[transaction_id]['t_dataitem'])
                         actions_taken.append(transaction_end_commit)
                         end_transaction(transaction_id,trans_state_commit,line)



        #if the operation is read or write
        elif operation == "r" or operation == "w":
            line1 = line.split(" ")
            transaction_id = line1[0][1]
            dataitem = line1[1][1]
    #Before processing an operation in the input list, check if the transaction is in a blocked state or aborted state

    #(i) If it is blocked, add the operation to the ordered list of the operations of that transaction that are waiting
        # to be executed, this operations will be executed once the transaction resumes
            if transaction_id in transaction_table:
                if transaction_table[transaction_id]['trans_state'] == 'blocked':
                    transaction_table[transaction_id]['waiting_operationslist'].append({'operation':operation, 'dataitem':dataitem})
                    lock_table[dataitem]['waiting_transactionslist'].append(transaction_id)

        #(ii) If the transaction has already been aborted, its subsequent operations in the input list are ignored.
                elif transaction_table[transaction_id]['trans_state'] == 'abort':
                    transaction_already_abort = "Line Operation " + line + \
                                             "Action Taken: transaction already aborted, status updated to " \
                                             + str(transaction_table[transaction_id]['trans_state']) + \
                                             ", TransactionId is " + str(transaction_id)
                    actions_taken.append(transaction_already_abort)                             #output list
        #If transaction is in active state, then it check if the operation is read or write and performs the functions as required
                elif transaction_table[transaction_id]['trans_state'] == 'active':
                    if operation == "r":
                        read_operation(line)
                    if operation == "w":
                        write_operation(line)

    print(transaction_table)
    print(lock_table)
    print(actions_taken)

#Writing the output into file
with open('output.txt','w') as out:
    for i in actions_taken:
        out.write(i)
        out.write("\n")
