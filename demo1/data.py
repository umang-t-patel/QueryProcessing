# Copyright (C) DomaniSystems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
'''
Get the description of all the Part of Speech Tag.
'''
pos_dict = {"ADJ": "adjective",
"ADP": "adposition",
"ADV": "adverb",
"AUX": "auxiliary verb",
"CONJ": "coordinating conjunction",
"DET": "determiner",
"INTJ": "interjection",
"NOUN": "noun",
"NUM": "numeral",
"PRT": "particle",
"PRON": "pronoun",
"PROPN": "proper noun",
"PUNCT": "punctuation",
"SCONJ": "subordinating conjunction",
"SYM": "symbol",
"VERB": "verb",
"X": "other"}

'''
Aggregation Data to Create JSON data for Database API
'''
agg_data = {'Sum' : [0,'sum','total','amount'],
'Min' : [1,'lowest','smallest','minimum'],
'Max' : [2,'biggest','greatest','largest','most','maximum'],
'Count' : [3,'how many','how much','number of','count'],
'Distinct Count' : [4],
'Average' : [5,'average','mean','normal'],
'Value' : [6,'what, value'],
'Top' : [7,'top','most','highest'],
'Bottom' : [8,'bottom','least']}

'''
Operator Data to Create JSON data for Database API
'''
operator_data = {'EqualTo' : [0, 'Equal To'],
'LessThan' : [1,'less than','below','less','lower than','under','before'],
'LessThanOrEqualTo' : [2, 'Less Than Or Equal To'],
'GreaterThan' : [3,'Greater Than','greater','larger','exceed','after','over','more than'],
'GreaterThanOrEqualTo' : [4,'Greater Than Or Equal To'],
'NotEqualTo' : [5,'Not Equal To', 'not','except'],
'StartsWith' : [6,'Starts With'],
'NotStartsWith' : [7,'Not Starts With'],
'EndsWith' : [8,'Ends With'],
'NotEndsWith' : [9,'Not Ends With'],
'Contains' : [10,'Contains'],
'NotContains' :[11,'Not Contains'],
'Between' : [12,'Between','in'],
'NotBetween' : [13,'Not Between'],
'OneOf' : [14,'One Of'],
'NotOneOf' : [15,'Not One Of']}

'''
Databse Schema
Database Table and Attributes
Table Name: Products, Orders, Categories and Employees
'''
table_data = {'Products':['Product|ProductID',
'ProductName|Product Name',
'SupplierID|SupplierID',
'CategoryID|CategoryID',
'QuantityPerUnit|Quantity Per Unit',
'UnitPrice|Unit Price',
'UnitsInStock|Units In Stock',
'UnitsOnOrder|Units On Order',
'ReorderLevel|Reorder Level',
'Discontinued|Discontinued']
,'Categories':['Categories|CategoryID',
'CategoryName|Category Name',
'Description|Description',
'Picture|Picture']
,'Orders':['OrderID|OrderID',
'CustomerID|CustomerID',
'EmployeeID|EmployeeID',
'OrderDate|Order Date',
'RequiredDate|Required Date',
'ShippedDate|Shipped Date',
'Shipvia|Ship via',
'Freight|Freight',
'ShipName|Ship Name',
'ShipAddress|Ship Address',
'ShipCity|Ship City',
'ShipRegion|Ship Region',
'ShipPostalCode|Ship Postal Code',
'ShipCountry|Ship Country']
,'Employees':['EmployeeID|EmployeeID',
'LastName|Last Name',
'FirstName|First Name',
'Title|Title',
'BirthDate|Birth Date',
'HireDate|Hire Date',
'Address|Address',
'City|City',
'Region|Region',
'PostalCode|Postal Code',
'Country|Country',
'HomePhone|Home Phone',
'Extension|Extension',
'Photo|Photo',
'Notes|Notes',
'ReportsTo|Reports To',
'PhotoPath|Photo Path']
}
'''
Table Mapping with Actual Database Table Name
'''
mapped_data={'Employees':'Employees_0','Orders':'Orders_0','Categories':'Categories_0','Products':'Products_0'}

'''
NER for Product Name
'''
ProductDetails=[
"Chai",
"Chang",
"Aniseed Syrup",
"Chef Anton's Cajun Seasoning",
"Chef Anton's Gumbo Mix",
"Grandma's Boysenberry Spread",
"Uncle Bob's Organic Dried Pears",
"Northwoods Cranberry Sauce",
"Mishi Kobe Niku",
"Ikura",
"Queso Cabrales",
"Queso Manchego La Pastora",
"Konbu",
"Tofu",
"Genen Shouyu",
"Pavlova",
"Alice Mutton",
"Carnarvon Tigers",
"Teatime Chocolate Biscuits",
"Sir Rodney's Marmalade",
"Sir Rodney's Scones",
"Gustaf's Knäckebröd",
"Tunnbröd",
"Guaraná Fantástica",
"NuNuCa Nuß-Nougat-Creme",
"Gumbär Gummibärchen",
"Schoggi Schokolade",
"Rössle Sauerkraut",
"Thüringer Rostbratwurst",
"Nord-Ost Matjeshering",
"Gorgonzola Telino",
"Mascarpone Fabioli",
"Geitost",
"Sasquatch Ale",
"Steeleye Stout",
"Inlagd Sill",
"Gravad lax",
"Côte de Blaye",
"Chartreuse verte",
"Boston Crab Meat",
"Jack's New England Clam Chowder",
"Singaporean Hokkien Fried Mee",
"Ipoh Coffee",
"Gula Malacca",
"Rogede sild",
"Spegesild",
"Zaanse koeken",
"Chocolade",
"Maxilaku",
"Valkoinen suklaa",
"Manjimup Dried Apples",
"Filo Mix",
"Perth Pasties",
"Tourtière",
"Pâté chinois",
"Gnocchi di nonna Alice",
"Ravioli Angelo",
"Escargots de Bourgogne",
"Raclette Courdavault",
"Camembert Pierrot",
"Sirop d'érable",
"Tarte au sucre",
"Vegie-spread",
"Wimmers gute Semmelknödel",
"Louisiana Fiery Hot Pepper Sauce",
"Louisiana Hot Spiced Okra",
"Laughing Lumberjack Lager",
"Scottish Longbreads",
"Gudbrandsdalsost",
"Outback Lager",
"Flotemysost",
"Mozzarella di Giovanni",
"Röd Kaviar",
"Longlife Tofu",
"Rhönbräu Klosterbier",
"Lakkalikööri",
"Original Frankfurter grüne Soße"]

'''
NER for Category Name
'''
CategoryDetails=["Beverages",
"Condiments",
"Confections",
"Dairy Products",
"Grains/Cereals",
"Meat/Poultry",
"Produce",
"Seafood"
]
