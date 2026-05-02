- Master DataSet, interpol·lació de les lectures.
    -> Per als trackers hi ha un problema, hi han lectures cada 6 hores.
       les interpolacions lineals no funcionen en aquest cas. Utilitzaré 
       pvlib per a millorar la interpol·lació
    -> He trobat que la variabilitat dels trackers ve donada per un periode
       on un grup de plaques es manté a un 50 graus. Despres d'aquest període
       es mouen igual. Podem utilitzar aquest període per fer un analisi de com
       canvia. Pero es molt curt aquest període, tenim poques dades i son només d'estiu.

       
- Model-Based RL per poder entendre el món.
