# importing app to route different web directories
from app import app
from flask import render_template, request, redirect, url_for
from .auth.forms import PokeForm, CatchForm
from .models import Team, User, CatchPokemon
from .myfunctions import  Pokemon_data, pokemon_pull, addPokemon, Battle
from flask_login import current_user, login_user, logout_user, login_required

# if url = localhost:5000/ call this function and return this
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    form = PokeForm()
    if request.method == "POST":
        if form.validate():
            name = form.pokemon.data.lower()
            # pokemon = CatchPokemon.query.filter_by(name=name)
            # pokemon_id = pokemon.id

            ### switch api pull to db pull!!!
            # pokemon = Pokemon_data(name)
            # pokemon_id = pokemon.id()

            

            # p_in_pokedex.clear()
            # p_in_pokedex.append(pokemon)

            # return redirect(url_for("pokedex", pokemon=pokedex, p=pokemon))
            return redirect(url_for("pokedex", name=name))
    return render_template("search.html", form=form)


@app.route('/pokedex/<name>', methods=["GET","POST"])
@login_required
def pokedex(name):
    if request.method == "POST":
        name=name.title()
        catch = CatchPokemon.query.filter_by(name=name).first()
        if catch:
            pokemon_id = catch.id
            if "catch" in request.form:
                return redirect(url_for('caught', pokemon_id=pokemon_id))
            elif "release" in request.form:
                return redirect(url_for('release', pokemon_id=pokemon_id))
    pokemon = Pokemon_data(name)
    pokemon_id = pokemon.id()
    poke = pokemon.pokedex()
    # flagging pokemon user already has
    my_catches = current_user.caught
    my_team = set()
    for c in my_catches:
        my_team.add(c.id)
    if pokemon_id in my_team:
        pokemon.flagged = "pokedex block: You already have this pokemon"

    return render_template("pokedex.html", p=pokemon, pokemon=poke)



# holds dashboard random pokemon in list for catching or releasing. Put rotation inside dash block as temp var 
# after POST branch - could make it a list rotation. Have post branch pull the 0 index of the list if list 
# existence == True
rotation = []
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    # fork code if POST request
    if request.method == "POST":
        if "catch" in request.form:
            print('Catch that pokemon!')
            print(current_user.get_id())

            # CatchPokemon(rotation[0]["name"], rotation[0]["stats"]["hp"], rotation[0]["stats"]["attack"], rotation[0]["stats"]["defense"], rotation[0]["sprite"], rotation[0]["cartoon"])
            # CatchPokemon(name, hp, attack, defense, sprite, cartoon) ^^
            # team_member = Team(rotation[0], current_user.get_id())
            # team_member.catch_pokemon()

            pokemon_id = rotation[0]["id"]
            return redirect(url_for('caught', pokemon_id=pokemon_id)) 

            ## first method for catching pokemon
            catch = CatchPokemon.query.filter_by(name=rotation[0]["name"]).first()
            my_catches = current_user.caught
            print(my_catches)
            print(catch)
            if len(my_catches) > 5:
                print("Your Pokemon Team is full!")
            else:
                if catch in my_catches:
                    print("You have already caught this Pokemon!")
                else:
                    catch.catch_it(current_user)
                    print(f"You caught {rotation[0]['name']}!")
                    return redirect(url_for('caught'))
        elif "release" in request.form:
            print("Release the pokemon!")
            pokemon_id = rotation[0]["id"]
            return redirect(url_for('release', pokemon_id=pokemon_id))
    
    # if GET request - pokemon_pull selects random pokemon name of the first 151 for pokemon banner
    name = pokemon_pull()
    # name = "staryu"
    pokemon = Pokemon_data(name)
    pokedex = pokemon.pokedex()
    rotation.append(pokedex)
    # rotation pokemon - the random pokemon generated in dashboard on every refresh
    if len(rotation) > 1:
        rotation.pop(0)

    # my_catches is all caught pokemon objects
        # getting number of caught pokemon and number of empty slots
    my_catches = current_user.caught
    num_catches = len(my_catches)
    empties = 5 - num_catches

    # flagging pokemon user already has > move?
    my_catches = current_user.caught
    my_team = set()
    for c in my_catches:
        my_team.add(c.id)
    if pokemon.id() in my_team:
        pokemon.flagged = "dash block: You already have this pokemon"
    print(my_team)
    print(pokemon.id())
    
    return render_template("dashboard.html", pokemon=pokedex, num_catches=num_catches, catches=my_catches, empties=empties, p=pokemon)

@app.route('/myteam', methods=["GET","POST"])
def team():
    if request.method == "POST":
        my_catches = current_user.caught
        print(request.form)
        for c in my_catches:
            if c.name in request.form:
                pokemon_id = c.id
                return redirect(url_for('release', pokemon_id=pokemon_id))
    # my_catches is all caught pokemon objects
        # getting number of caught pokemon and number of empty slots
    my_catches = current_user.caught
    if my_catches:
        num_catches = len(my_catches)
        empties = 5 - num_catches
        top_catch = my_catches[0]

    return render_template("myteam.html", num_catches=num_catches, catches=my_catches, empties=empties, top=top_catch)

# @app.route('/caught')
# @login_required
# def caught():
#     info = rotation[0].copy()
#     return render_template('caught.html', pokemon=info)

@app.route('/caught/<int:pokemon_id>')
@login_required
def caught(pokemon_id):
    # check works
    if len(current_user.caught) == 5:
        print("caught block: You've reached maximum pokemon limit. Release a pokemon to add more")
        return redirect(url_for('dashboard'))
    else:
        catch = CatchPokemon.query.get(pokemon_id)

        # check already team may not be needed since catch button is conditionally rendered
        my_catches = current_user.caught
        my_team = set()
        for c in my_catches:
            my_team.add(c.id)
        if pokemon_id in my_team:
            print("caught block: You've already caught this pokemon")
            return redirect(url_for('dashboard'))
        
        print("caught block: We are going to catch this pokemon")
        catch.catch_it(current_user)
        return render_template('caught.html', pokemon=catch)


@app.route('/release/<int:pokemon_id>')
@login_required
def release(pokemon_id):
    pokemon = CatchPokemon.query.get(pokemon_id)
    pokemon.release_it(current_user)
    return redirect(url_for('team'))

@app.route('/battle', methods=["GET", "POST"])
def battle():
    users = User.query.all()
    return render_template('battle.html', all_users=users)

@app.route('/myaccount')
def account():
    return render_template('account.html')

@app.route('/arena/<int:user_id>')
def arena(user_id):
    my_catches = current_user.caught
    opponent = User.query.get(user_id)
    if request.method == "POST":
        return redirect(url_for('arean_results', user_id=user_id))
    return render_template('arena.html', catches=my_catches, opp=opponent)

@app.route('/arena-results/<int:user_id>')
def arena_results(user_id):
    my_catches = current_user.caught
    opponent = User.query.get(user_id)
    user = {"name": "user", "hp": 0, "attack": 0 , "defense": 0}
    opp = {"name": "opponent", "hp": 0, "attack": 0 , "defense": 0}
    for c in my_catches:
        if user["hp"] == 0:
            user["hp"] = c.hp
        else:
            user["hp"] += c.hp
        if user["attack"] == 0:
            user["attack"] = c.attack
        else:
            user["attack"] += c.attack
        if user["defense"] == 0:
            user["defense"] = c.defense
        else:
            user["defense"] += c.defense
    for c in opponent.caught:
        if opp["hp"] == 0:
            opp["hp"] = c.hp
        else:
            opp["hp"] += c.hp
        if opp["attack"] == 0:
            opp["attack"] = c.attack
        else:
            opp["attack"] += c.attack
        if opp["defense"] == 0:
            opp["defense"] = c.defense
        else:
            opp["defense"] += c.defense


    print(user, opp)
    battle = Battle(user, opp)
    print(battle.run())
    if battle.winner == "user":
        print("User wins")
    elif battle.winner == "opponent":
        print("opponent wins")
    
    return render_template('arena-results.html', catches=my_catches, opp=opponent, battle=battle)

@app.route('/friend-request')
def friend_request():
    return "Friend request feature not yet implented"

@app.route('/friends')
def friends():
    return "Friends page not yet done"