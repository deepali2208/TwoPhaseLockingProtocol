#Project- Part1 PsuedoCode for Concurrency Control
#Sadhana Singh - 1001460273
#Deepali Kumar - 1001429496

#Notes:
#Read_Lock equivalent to "Shared Lock"
#Write_Lock equivalent to "Exclusive Lock"

#Check for deadlock prevention protocol using wait-die rules to determine if the transaction should wait (be blocked) or die (abort)
#The transaction timestamps are used to decide on which action to take

def waitdie(transaction1, transaction2,lineinput):                                  #function to check waitdie condition
    if timestamp(transaction1) < timestamp(transaction2):
        transaction1 waits                                                          
        Add transaction1 operations to transaction_table.waiting_operationslist     #add transaction operations to transaction_table
        Add waiting transactions in lock_table.waiting_transactionslist             #add waiting transactions in lock_table
        Set state = "blocked"
        return "b"
    else:
        transaction1 dies
        Call function endtransaction(lineinput)                                     #call function endtransaction to unlock all items
        Set state = "abort"
        return "a"

#Process of committing and aborting transaction should release (unlock) any items that are currently locked by the transaction one at a time
#below function unlocks all the items 
#The process of unlocking an item should check if any transaction(s) are blocked because of waiting for the item. 
#If any transactions are waiting, it should remove the first waiting transaction and grant it access to the item and resume the transaction. 
#All waiting operations of the transaction are processed

def endtransaction(lineinput):
    d = lineinput.data_item 
    op = lineinput.operations
    t_id = lineinput.transactions
    
    for items in lock_table.transactionid_list:                                     #for loop: for all data_item of transactions that is to be Committed or aborted
        locked_item = Get row from lock_table of that transactions                  
        Unlock items.data_item locked by transaction                                #Unlocks the items

        #Checking any transactions are waiting for that data item
        #removes the first waiting transaction
        result1 = Pop from lock_table.waiting_transactionslist for items.data_item              #Get first transactionid form waiting_transactionslist which is like r1(x);w1(x)
        if result1 is read operation:
            Pop all the next "read" operations in lock_table.waiting_transactionslist           #Get all read as read need not wait as it is Shared lock
            Grant "Read_Lock" to all the read operations                                                #grant it access to the item
            add all the read operation transactions in lock_table.transactionid_list            
            Set transaction_state = "active" in transaction_table for all the transactions              #resume the transaction to active

        elif result1 is Write operation:
            Pop next "Write" operation in lock_table.waiting_transactionslist                   #removes the first waiting transaction
            Grant "Write_Lock" to Write operations                                              #grant it access to the item
            add Write operation transactions in lock_table.transactionid_list            
            Set transaction_state = "active" in transaction_table for that transactions         #resumes the transaction to active    



def main():
    for input in file:
        t_id = transactionid    // for eg: 1 from r1(x)
        d = data_item           // for eg: x from r1(x)
        op = operations         // for eg: r from r1(x)
        lineinput = input

        #transaction record should be created in the transaction table when a begin transaction operation (b) is processed 
        #(the state of this transaction should be active).
        if op == "b":
            Insert entry into transaction_table                         #transaction created
            Set transaction_id = t_id,timestamp = timestamp of transaction, transaction_state = "active" and t_checkgrowingphase = "True"   # Set to active

            #the operations are updated in the waiting_operationslist when status is blocked
            if transaction_state is "blocked":
                add operations(lineinput) in transaction_table.waiting_operationslist

            #Any subsequent operations of the aborted transaction that are read from the input file should be ignored if the state is abort
            elif transaction_state is "abort":
                ignore all subsequent operations for that transactions
            elif transaction_state is "active":
                switch(op):
                    #Processing a read operation and the appropriate read lock(X) request is set and the lock table is updated appropriately
                    case "r":
                        if transaction_table.t_checkgrowingphase = True:                    #check whether the schedule is in growing phase
                            item = Get row from lock_table of that data_item(d)             # Get row for data_item(x) from lock_table for eg:"x"
                            #If the item is already locked by a non-conflicting read lock, 
                            #the transaction is added to the list of transactions that hold the read lock on the requested item (in the lock table).
                            if item.data_item exists in lock_table:
                                if item.lock_state is "Read_Lock":                          #checking for non conflicting read lock
                                    if item.t_id not in item.transactionid_list:            # checking whether transaction exists in the transactionlist in the lock table
                                        add item.t_id in item.transactionid_list            #If not exists, add to the list

                                #If the item is already locked by conflicting Write-Lock then the wait die protocol determines whether the transactions are to be 
                                #blocked or aborted
                                elif item.lock_state is  "Write_Lock":                      
                                    if item.t_id != item.transactionid_list                 #In case of Conflicting Write Lock
                                    waitdie(item.transactionid_list, t_id)
                            else:
                                insert entry into lock_table                                #Insert the data item if it does not exists in lock table
                                Set data_item = "d", lock_state = "Read_Lock",transactionid_list = "t_id",waiting_transactionslist = None
                                update entry in transaction table for transaction_table.data_item = "d"


                    #Processing a write operation, first check whether the schedule is in Growing phase, we are maintaining the boolean field "t_checkgrowingphase"
                    #in the transaction table to track whether the schedule is in growing phase or not, it will permit upgrade only in growing phase

                    case "w":
                        if transaction_table.t_checkgrowingphase = True:                    #check whether the schedule is in growing phase
                            item = Get row from lock_table for that data_item(d)            # Get row for data_item(x) from lock_table for eg:"x"

                            #lock upgrading is permitted if the upgrade conditions are met
                            # if the item is read locked by only the transaction that is requesting the write lock, it is upgrade to write lock
                            if item.data_item exists in lock_table:
                                if item.lock_state is "Read_Lock":                          #Non Conflicting Read Lock
                                    if item.t_id in item.transactionid_list:
                                        if len(item.transactionid_list) == 1:
                                            upgrade from "Read_Lock" to "Write_Lock"                                        
                                        else:
                            #If the item is already locked by a conflicting read lock, then wait-die protocol determines the state of transaction
                            #It check for all the transactions in the list, even if one aborts then the it breaks the for loop
                                            for t in item.transactionid_list:               
                                                waitdieresults = waitdie(t_id, t)           
                                                if waitdieresults == "a":
                                                    break "for" loop
                            #If the item is already locked by a conflicting Write lock, then wait-die protocol determines the state of transaction
                                elif item.lock_state is "Write_Lock":
                                    if item.t_id != item.transactionid_list                 #In case of Conflicting Write Lock
                                    waitdie(item.transactionid_list,t_id)
                            else:
                                insert entry into lock_table                                #Insert the data item if it does not exists in lock table
                                Set data_item = "d", lock_state = "Write_Lock",transactionid_list = "t_id",waiting_transactionslist = None 
                                update entry in transaction table for transaction_table.data_item = "d"         #update the transaction table entry for dataitemlist 
                                                                                                                # as new entry is added in the lock table for that transaction

                     #Processing when transaction reaches its end (e) operation successfully, it should be committed                                                                                                   
                    case "e":
                        endtransaction(lineinput)                                               #endtransaction is different method to unlock all items 
                        Set transaction_table.transaction_state == "Committed"                  #Set transaction state to committed



Data Structures Used 
----------------------------------------

transaction_table, lock_table will be arraylist

Each entry in the transaction_table and lock_table is a dictionary

transaction_table structure is as follows:
dictionary:{transaction_id: int, transaction_state: String, data_item:arraylist, waiting_operationslist: linkedlist, t_checkgrowingphase: boolean}


lock_table structure is as follows:
dictionary:{data_item: String,lock_state: String, transactionid_list: arraylist, waiting_transactionslist: doublylinkedlist}





