1. Listar Cuentas

"""
Obtener todas las cuentas del comercio actual, formatear el resultado en una tabla de texto (tabular)
"""

2. Obtener Transacciones de Cuenta

"""
Obtener todas las transacciones de una cuenta de comercio mediante account_id, formatear el resultado en una tabla de texto (tabular)

(ID corto: solo los primeros 8 caracteres, igual que el campo "reference", y enmascarar la cuenta de destino)

3. Listar Clientes

"""
Obtener todos los clientes del comercio actual, formatear el resultado en una tabla de texto (tabular)
"""

4. Obtener Detalles del Cliente

"""
Obtener los detalles de un cliente por customer_id, formatear el resultado en una tabla de texto (tabular)
"""

4.1. Crear Cliente

"""
Crear un cliente:
- tax_id_type: rfc
- tax_id: BTA160616Q24
- name: BANCO DE TAPITAS AC
- external_id: "PROM001.BTA"
- withdrawal_accounts: 
    account_number: 012680001108499959
    bicfi: BCMRMXMM
    selected: true
"""

4.2. Crear Cliente  - ERROR

"""
Crear un cliente:
- tax_id_type: rfc
- tax_id: CES100720PY9
- name: Construyendo Esperanzas, A.C.
- external_id: "PROM003.CES"
- withdrawal_accounts: 
    account_number: 012290001107697557
    account_format: "clabe"
    bicfi: BCMRMXMM
    selected: true
"""

4.3. Crear Cliente  - ERROR

"""
Crear un cliente:
- tax_id_type: rfc
- tax_id: CVN100202RHA
- name: Campeones de la Vida NR, A.C.
- external_id: "PROM003.CES"
- withdrawal_accounts: 
    account_number: 012320001100980784
    account_format: "clabe"
    bicfi: BCMRMXMM
    selected: true
"""

5. Transferencia

"""
Quiero transferir 0.01 MXN a ese cliente, origen: ea530790-bddb-4bfe-95b7-410ca1ec6e7e
"""

5.1. Verificar Estado de Transferencia

"""
Obtener el estado de una transferencia mediante transfer_id, formatear el resultado en una tabla de texto (tabular)
"""

6. Cobros

"""
Debo cobrar a mis clientes (de la lista de clientes, guardar el customer_id uuid), 10 MXN por los servicios de la empresa. Crear un intento de cobro para los clientes que tengan al menos una cuenta de retiro. Usar como destino: ea530790-bddb-4bfe-95b7-410ca1ec6e7e.

Devolver una lista de customers.external_id y la cuenta virtual asignada a cada cliente.
"""
