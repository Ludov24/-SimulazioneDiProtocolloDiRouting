import datetime
import time
import os

start_time = time.time()


class Node:
    def __init__(self, name):
        self.name = name
        self.routingTable = {name: (0, name)} 
        self.neighbors = {} 

    def updateRoutingTable(self, neighborName, neighborTable):
        """
        Aggiorna la tabella di routing basata sulle informazioni ricevute dal vicino.
        """
        updated = False
        for destination, (neighborCost, nextHop) in neighborTable.items():
            if destination == self.name: 
                continue
            current_cost, currentHop = self.routingTable.get(destination, (float('inf'), None))
            new_cost = self.neighbors[neighborName] + neighborCost
            if new_cost < current_cost:
                self.routingTable[destination] = (new_cost, neighborName)
                updated = True 
        return updated

    def shareTable(self):
        """
        Condivide la propria tabella di routing con i vicini.
        """
        return self.routingTable

    def disconnectNeighbor(self, neighborName):
        """
        Simula un guasto disconnettendo un vicino.
        
        Aggiorna il costo verso il vicino disconnesso a infinito (inf)
        e lo rimuove dalla tabella di routing.

        Argomenti:
            neighborName (str): Nome del nodo vicino da disconnettere.

        """

        if neighborName in self.neighbors:
            self.neighbors[neighborName] = float('inf')  # Costo infinito
            self.routingTable[neighborName] = (float('inf'), None)

    def __str__(self):
        """
        Stampa il nodo e la sua tabella di routing.
        """
        table = "\n".join([f"{dest}: cost {cost}, next hop {hop}" for dest, (cost, hop) in self.routingTable.items()])
        return f"Node {self.name} Routing Table:\n{table}"


class Network:
    def __init__(self):
        self.nodes = {}

    def addNode(self, name):
        """
        Aggiunge un nuovo nodo alla rete.
        """
        self.nodes[name] = Node(name)

    def connectNodes(self, node1, node2, cost):
        """
        Connette due nodi con un collegamento bidirezionale.
        """
        if node1 in self.nodes and node2 in self.nodes:
            self.nodes[node1].neighbors[node2] = cost
            self.nodes[node2].neighbors[node1] = cost
            self.nodes[node1].routingTable[node2] = (cost, node2)
            self.nodes[node2].routingTable[node1] = (cost, node1)

    def simulateIteration(self):
        """
        Simula un'iterazione del protocollo RIP.
        
        Ogni nodo condivide la propria tabella di routing con i vicini e 
        aggiorna la propria tabella in base alle informazioni ricevute.

        Ritorna:
            bool: True se almeno una tabella di routing è stata modificata, False altrimenti.
        """
        
        updated = False
        for nodeName, node in self.nodes.items():
            for neighborName in node.neighbors.keys():
                if neighborName in self.nodes:
                    updated |= node.updateRoutingTable(neighborName, self.nodes[neighborName].shareTable())
        return updated

    def simulateFailure(self, node1, node2):
        """
        Simula un guasto tra due nodi, disconnettendo il collegamento.

        Argomenti:
            node1 (str): Nome del primo nodo coinvolto nel guasto.
            node2 (str): Nome del secondo nodo coinvolto nel guasto.
        """

        if node1 not in self.nodes or node2 not in self.nodes:
            print(f"Errore: {node1} o {node2} non esiste nella rete.")
            return
        self.nodes[node1].disconnectNeighbor(node2)
        self.nodes[node2].disconnectNeighbor(node1)

    def logRoutingTables(self, filename, event=""):
        """
        Registra lo stato delle tabelle di routing in un file di log con timestamp.

        Argomenti:
            filename (str): Nome del file di log.
            event (str, opzionale): Descrizione dell'evento da registrare. Default "".
        """

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Controlla se il file esiste già
        file_exists = os.path.isfile(filename)
        with open(filename, "a") as log_file:
            # Aggiungi l'intestazione se il file è nuovo
            if not file_exists:
                log_file.write("Log della Simulazione del Protocollo RIP\n")
                log_file.write("=" * 40 + "\n")
                log_file.write("Questo file contiene le tabelle di routing e gli eventi registrati durante la simulazione.\n")
                log_file.write("Ogni voce include un timestamp e una descrizione dell'evento.\n")
                log_file.write("=" * 40 + "\n\n")
            
            log_file.write(f"\n[{timestamp}] {event}\n")
            log_file.write("-" * 40 + "\n")
            for node_name, node in self.nodes.items():
                log_file.write(f"Routing Table for Node {node_name}:\n")
                log_file.write("{:<12} {:<10} {:<10}\n".format("Destination", "Cost", "Next Hop"))
                log_file.write("-" * 34 + "\n")
                for dest, (cost, hop) in node.routingTable.items():
                    hop = hop if hop is not None else "N/A"
                    log_file.write("{:<12} {:<10} {:<10}\n".format(dest, cost, hop))
                log_file.write("-" * 40 + "\n")


    def printRoutingTables(self):
        """
        Stampa le tabelle di routing di tutti i nodi nella rete in formato tabellare.
        """
        for node_name, node in self.nodes.items():
            print(f"Routing Table for Node {node_name}:")
            print("{:<12} {:<10} {:<10}".format("Destination", "Cost", "Next Hop"))
            print("-" * 34)
            for dest, (cost, hop) in node.routingTable.items():
                # Sostituisci None con "N/A" per evitare errori
                hop = hop if hop is not None else "N/A"
                print("{:<12} {:<10} {:<10}".format(dest, cost, hop))
            print("-" * 40)


# Creazione della rete
network = Network()
network.addNode('A')
network.addNode('B')
network.addNode('C')

# Connessioni tra i nodi
network.connectNodes('A', 'B', 1)
network.connectNodes('B', 'C', 1)
network.connectNodes('A', 'C', 4)

# Nome del file di log
log_file = "networkLog.txt"

# Stato iniziale
print("\n" + "=" * 40 + "\nStato iniziale della rete:")
network.printRoutingTables()
network.logRoutingTables(log_file, event="Stato iniziale della rete")
start_time_initial = time.time()

# Misura del tempo di convergenza iniziale
print("\n" + "=" * 40 + "\nSimulazione del protocollo RIP (iniziale):")
for iteration in range(100):  # Limita a 100 iterazioni per sicurezza
    print(f"\nIterazione {iteration + 1}:")
    updated = network.simulateIteration()
    network.printRoutingTables()
    network.logRoutingTables(log_file, event=f"Iterazione {iteration + 1} (iniziale)")
    if not updated:
        print(f"La rete è convergente dopo {iteration + 1} iterazioni.")
        break
    if iteration == 99:
        print("Attenzione: la rete non è convergente dopo 100 iterazioni.")

end_time_initial = time.time()  # Fine tempo simulazione iniziale
print(f"Tempo totale per la convergenza iniziale: {end_time_initial - start_time_initial:.2f} secondi")


# Simula un guasto tra A e B
print("\n" + "=" * 40 + "\nSimulazione di un guasto (link A-B interrotto):")
network.simulateFailure('A', 'B')
network.printRoutingTables()
network.logRoutingTables(log_file, event="Guasto tra A e B")

print("\n" + "=" * 40 + "\nSimulazione del protocollo RIP (dopo il guasto):")
start_time_post_failure = time.time()

# Simulazione del RIP dopo il guasto
print("\n" + "=" * 40 + "\nSimulazione del protocollo RIP (dopo il guasto):")
for iteration in range(100):  # Limita a 100 iterazioni per sicurezza
    print(f"\nIterazione {iteration + 1}:")
    updated = network.simulateIteration()
    network.printRoutingTables()
    network.logRoutingTables(log_file, event=f"Iterazione {iteration + 1} (dopo guasto)")
    if not updated:
        print(f"La rete è convergente dopo {iteration + 1} iterazioni.")
        break
    if iteration == 99:
        print("Attenzione: la rete non è convergente dopo 100 iterazioni.")

end_time_post_failure = time.time()  # Fine tempo simulazione post-guasto
print(f"Tempo totale per la convergenza dopo il guasto: {end_time_post_failure - start_time_post_failure:.2f} secondi")


total_time = (end_time_initial - start_time_initial) + (end_time_post_failure - start_time_post_failure)
print(f"Tempo totale per l'intera simulazione: {total_time:.2f} secondi")
network.logRoutingTables(log_file, event=f"Tempo totale per l'intera simulazione: {total_time:.2f} secondi")

