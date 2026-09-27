"""Narration script for "The Battle of the Somme, 1916".

Each segment is a chapter; sentences are voiced separately so shots can cut on
sentence boundaries and captions are exact. Every figure is sourced in
RESEARCH.md.
"""

SEGMENTS = [
    {
        "id": "open",
        "chapter": "Introduction",
        "sentences": [
            "On the first of July, 1916, at half past seven in the morning, whistles blew along "
            "the British front in northern France.",
            "By nightfall, the British Army had suffered more casualties than on any other day in "
            "its history.",
            "This is the story of the Battle of the Somme.",
        ],
    },
    {
        "id": "stalemate",
        "chapter": "Stalemate",
        "sentences": [
            "By 1916, the Western Front was a line of trenches running from the Channel coast to "
            "the Swiss border.",
            "In December 1915, at Chantilly, the Allies agreed to strike together in the new year, "
            "with a great Anglo-French offensive astride the River Somme.",
        ],
    },
    {
        "id": "verdun",
        "chapter": "Verdun Changes the Plan",
        "sentences": [
            "But in February, Germany attacked the French at Verdun.",
            "As French divisions were drawn into that battle, the Somme became a mainly British "
            "offensive, with a new purpose: to relieve the pressure on Verdun.",
        ],
    },
    {
        "id": "army",
        "chapter": "Kitchener's Army",
        "sentences": [
            "Britain's small professional army had been joined by hundreds of thousands of "
            "volunteers who answered Lord Kitchener's call.",
            "Many served in Pals battalions: friends, neighbours and workmates from the same "
            "towns, who had enlisted together, and would fight together.",
        ],
    },
    {
        "id": "bombardment",
        "chapter": "The Bombardment",
        "sentences": [
            "The plan, under Sir Douglas Haig and General Rawlinson's Fourth Army, rested on "
            "artillery.",
            "From the twenty-fourth of June, British guns fired more than one and a half million "
            "shells.",
            "It was not enough. Most were shrapnel, useless against deep dugouts, and as many as "
            "a third failed to explode.",
            "Much of the barbed wire survived. And the Germans waited, underground.",
        ],
    },
    {
        "id": "zero",
        "chapter": "Zero Hour: 1 July 1916",
        "sentences": [
            "At twenty past seven, a mine exploded beneath Hawthorn Ridge.",
            "At seven twenty-eight, more mines tore open the German line, among them the vast "
            "Lochnagar mine at La Boisselle.",
            "At seven thirty, the infantry climbed out of their trenches, and the German machine "
            "gunners ran up from their dugouts to meet them.",
        ],
    },
    {
        "id": "slaughter",
        "chapter": "The First Day",
        "sentences": [
            "At Serre, the Accrington Pals lost 585 of about 720 men in half an hour.",
            "At Beaumont-Hamel, 801 men of the Newfoundland Regiment went forward. Only 68 "
            "answered the next roll call.",
            "In the south, British and French troops took most of their objectives, including "
            "Montauban and Mametz.",
            "But by nightfall, the British had suffered 57,470 casualties, 19,240 of them killed.",
        ],
    },
    {
        "id": "attrition",
        "chapter": "Attrition",
        "sentences": [
            "There was no breakthrough. The battle became a grinding struggle of attrition.",
            "On the fourteenth of July, a surprise dawn attack took Bazentin Ridge.",
            "South Africans held Delville Wood for six days; of more than three thousand men, 780 "
            "came out.",
            "At Pozières, the Australians suffered 23,000 casualties in under seven weeks.",
        ],
    },
    {
        "id": "tanks",
        "chapter": "The First Tanks",
        "sentences": [
            "On the fifteenth of September, at Flers-Courcelette, Britain unveiled a new weapon: "
            "the tank.",
            "Of forty-nine, thirty-two reached the start line, and only eighteen went into "
            "action. But one led the infantry up the main street of Flers.",
        ],
    },
    {
        "id": "mud",
        "chapter": "Autumn and Mud",
        "sentences": [
            "Thiepval, an objective for the first day, finally fell on the twenty-sixth of "
            "September.",
            "Then the rains came, and the battlefield dissolved into mud.",
            "Beaumont-Hamel was taken at last on the thirteenth of November. Five days later, in "
            "sleet and snow, the offensive was halted.",
        ],
    },
    {
        "id": "cost",
        "chapter": "The Cost",
        "sentences": [
            "In 141 days, the Allies had advanced no more than seven miles.",
            "The British Empire suffered some 420,000 casualties, the French about 200,000, and "
            "the Germans at least 450,000.",
        ],
    },
    {
        "id": "legacy",
        "chapter": "Legacy",
        "sentences": [
            "Was it a futile slaughter, or a costly but necessary step towards victory? "
            "Historians still argue.",
            "The German army had been badly worn down. A German staff officer called the Somme "
            "the muddy grave of the German field army, and in early 1917 it withdrew to the "
            "Hindenburg Line.",
            "Today, the Thiepval Memorial bears the names of more than 72,000 British and South "
            "African men who have no known grave.",
            "The fields have long been ploughed. But every summer, the poppies return.",
        ],
    },
]
