# Simulador-IAM-con-RBAC
### Gestió d'identitats i accessos basada en rols

> **Anàlisi i Disseny d'Algoritmes Avançats — Projecte Grupal AA4**
> 
Joan Cobos, Roc Reverté i Daniel Baena

## 1. Nom del projecte

**Simulador IAM amb RBAC** 


## 2. Descripció breu

El nostre grup hem fet un sistema que simula la gestió centralitzada d'identitats i accessos d'una organització. Controla quins usuaris poden accedir a quins recursos en funció dels rols que tenen assignats, amb us  d'herència dels rols i log d'auditoria. Resol el problema real de la gestió manual d'accessos empresarials, que és lenta, poc escalable i propensa a errors i accessos no autoritzats.


## 3. Integrants del grup

Nom i cognoms    
    Joan Cobos       
    Roc Reverté       
    Daniel Baena      

* Abans de continuar explicar que Daniel Baena te la gran majoria de commits ja que no ha pogut participar en el video demostratiu, per tant per igualar la carrega de treball hem decidit fer aixo, recalcar que tots hem treballat per igual en la idealització i posada en marxa del nostre projecte final.

## 4. Context i problemàtica

En entorns empresarials, controlar qui accedeix a cada recurs és critic i pot suposar un perill no fer-ho de manera correcta. La gestió manual d'accessos individual per usuari no escala i genera errors de seguretat. RBAC soluciona aquest problema assignant permisos a rols en lloc de a usuaris directament, i permetent que els rols heretin permisos dels seus rols pare, jerarquia. Sistemes com Active Directory, Keycloak i Azure AD segueixen exactament aquest paradigma.

## 5. Funcionalitats principals

- Creació, consulta i eliminació d'usuaris, rols i recursos
- Assignació i revocació de rols a usuaris
- Assignació de permisos a rols
- Herència jeràrquica de rols (un rol hereta els permisos del seu pare)
- Verificació d'accés: comprova si un usuari pot accedir a un recurs
- Interfície CLI interactiva amb escenari de demo precarregat
- Benchmark empíric de complexitat
- Suite de 26 tests unitaris

## 6. Ús de POO i polimorfisme

### Jerarquia de classes

Entitat:  Usuario te un Rol que te acces a Recurso

IAMSystem  (motor central, gestiona les tres entitats)

### On s'aplica el polimorfisme

- La classe abstracta Entitat defineix els mètodes describir() i tipo() com a abstractes.
- Cada subclasse (Usuario, Rol, Recurso) els implementa de forma diferent.
- IAMSystem pot cridar entitat.describir() sense saber de quin tipus concret es tracta → polimorfisme com s'ens demana.
- El mètode __eq__ i __hash__ es defineixen a Entitat i funcionen per a totes les subclasses.

### Recursivitat

- Rol.tiene_permiso(permiso, visitados) — crida recursivament al _padre fins trobar el permís o arribar a l'arrel.
- Rol.obtener_todos_permisos(visitados) — acumula permisos de tota la cadena d'herència recursivament.
- Ambdues funcions porten un set de visitados per evitar cicles infinits.

### Estructures de dades

 dict (taula hash) --> Usuaris, rols, recursos per nom -- >O(1) accés 

 set (taula hash) -->   Permisos per rol, rols per usuari --> O(1) inserció/cerca, sense duplicats 

 list -->  Log d'auditoria --> O(1) append, O(n) lectura 

 Arbre de punters --> Jerarquia de rols (_pare) --> O(h·p) recorregut recursiu 