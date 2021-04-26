import os
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request
from base64 import b64encode

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://baudgkhojtusou:1b872740b3a79aaaf9d03214b433dfd69b2e770afb370b9569a9509e5a03aadb@ec2-107-22-83-3.compute-1.amazonaws.com:5432/d81ld18t7tofq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)
api = Api(app)
parser = reqparse.RequestParser()


##############################

class Artist(db.Model):
    Id = db.Column(db.String(200),primary_key=True)
    name = db.Column(db.String(200))
    age = db.Column(db.Integer)
    albums = db.relationship('Album', backref='artist', lazy=True)
    #album_id = db.relationship('Album', backref='artist', lazy=True)

    def __init__(self,Id,name,age):
        self.Id = Id
        self.name = name
        self.age = age

    def json(self):
        return {"id": self.Id, "name": self.name, "age": self.age}

class Album(db.Model):
    Id = db.Column(db.String(200),primary_key=True)
    artist_id = db.Column(db.String(200), db.ForeignKey('artist.Id'), nullable=False)    
    name = db.Column(db.String(200))
    genre = db.Column(db.String(200))
    tracks = db.relationship('Track', backref='album', lazy=True)

    def __init__(self,Id,artist_id,name,genre):
        self.Id = Id
        self.artist_id = artist_id
        self.name = name
        self.genre = genre

    def json(self):
        return {"id": self.Id, "artist_id": self.artist_id,"name": self.name, "genre": self.genre}

class Track(db.Model):
    Id = db.Column(db.String(200),primary_key=True)
    album_id = db.Column(db.String(200), db.ForeignKey('album.Id'), nullable=False)   
    name = db.Column(db.String(200))
    duration = db.Column(db.Float)
    times_played = db.Column(db.Integer)

    def __init__(self,Id,album_id,name,duration,times_played):
        self.Id = Id
        self.album_id = album_id
        self.name = name
        self.duration = duration
        self.times_played = times_played

    def json(self):
        return {"id": self.Id, "album_id": self.album_id, "name": self.name, "duration": self.duration, "times_played": self.times_played}

##############################

class ArtistNames(Resource):
    def get(self):    
        arts = Artist.query.all()
        if arts:
            lista = []
            lista_art = []
            for art in arts:
                lista_art = art.json()
                identificador = lista_art['id']
                lista_art['albums'] = f'https://tarea2-taller.herokuapp.com/artists/{identificador}/albums'
                lista_art['tracks'] = f'https://tarea2-taller.herokuapp.com/artists/{identificador}/tracks'
                lista_art['self'] = f'https://tarea2-taller.herokuapp.com/artists/{identificador}'   
                lista.append(lista_art)
            return lista
        else:
            return {'name':None},404
    
    def post(self):
        lista = []
        #print("------------parser antes de add argument", parser.parse_args())
        parser.add_argument('name', action='append')
        parser.add_argument('age', action='append')
        #print("------------parser despues de add argument", parser.parse_args())
        args = parser.parse_args()
        #print("---------args",args)
        if args['name'] == None or args['age'] == None:
            return {"input": "invalido"},400
        nombre = args['name'][0]
        edad = args['age'][0]
        id_encoded = b64encode(nombre.encode()).decode('utf-8')[:22]        
        albumsurl = f'https://tarea2-taller.herokuapp.com/artists/{id_encoded}/albums'
        tracksurl = f'https://tarea2-taller.herokuapp.com/artists/{id_encoded}/tracks'
        selfurl = f'https://tarea2-taller.herokuapp.com/artists/{id_encoded}'
        arts = Artist.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            nombre_pos = lista[pos]['name']
            edad_pos = lista[pos]['age']
            if identificador == id_encoded:
                return {"id": identificador, "name": nombre_pos, "age": edad_pos, "albums": albumsurl, "tracks": tracksurl, "self": selfurl},409
        artista = Artist(id_encoded,nombre,edad)
        db.session.add(artista)
        db.session.commit()
        return {"id": id_encoded, "name": nombre, "age": edad, "albums": albumsurl, "tracks": tracksurl, "self": selfurl},201

#api.add_resource(ArtistNames, 'https://tarea2-taller.herokuapp.com/artists')
api.add_resource(ArtistNames, '/artists')

class ArtistId(Resource):
    def get(self,Id):
        lista = []
        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{Id}/albums'
        tracksurl = f'https://tarea2-taller.herokuapp.com/artists/{Id}/tracks'
        selfurl = f'https://tarea2-taller.herokuapp.com/artists/{Id}' 
        arts = Artist.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            nombre_pos = lista[pos]['name']
            edad_pos = lista[pos]['age']
            if identificador == Id:
                return {"id": identificador, "name": nombre_pos, "age": edad_pos, "albums": artisturl, "tracks": tracksurl, "self": selfurl}
        return {'artista':'inexistente'},404

    def delete(self,Id):
        lista_artist = []
        lista_artista = []
        lista = []
        lista_track = []
        lista_album = []
        lista_canciones = []
        artista = Artist.query.all()
        for arti in artista:
            lista_artist.append(arti.json())
        for posi in range(len(lista_artist)):
            identificador_artista = lista_artist[posi]['id']
            if identificador_artista == Id:
                borrar_artista = Artist.query.get({'Id': Id})
                lista_artista.append(Id)
        albums = Album.query.all()
        for art in albums:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            nombre_album = lista[pos]['name']
            #artista_id = lista[pos]['artist_id']
            nombre_encriptar = nombre_album + ':' + Id
            id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
            if identificador == id_encode:
                borrar_album = Album.query.get({'Id': identificador}) 
                lista_album.append(Id)
                id_encoded = id_encode
        tracks = Track.query.all()
        for tra in tracks:
            lista_track.append(tra.json())
        for pos in range(len(lista_track)):
            identificador_track = lista_track[pos]['id']
            alb_id = lista_track[pos]['album_id']
            if alb_id == id_encoded:
                borrar_track = Track.query.get({'Id': identificador_track}) 
                lista_canciones.append(Id)
        
        if Id in lista_artista:
            db.session.delete(borrar_artista)

        if Id in lista_album:
            db.session.delete(borrar_album)

        if Id in lista_canciones:
            db.session.delete(borrar_track)

        db.session.commit()
        if Id in lista_album or Id in lista_canciones or Id in lista_artista:
            return {'artista':'eliminado'},204
        else:
            return {'artista':'inexistente'},404   
   

#api.add_resource(ArtistId, 'https://tarea2-taller.herokuapp.com/artists/<string:Id>')
api.add_resource(ArtistId, '/artists/<string:Id>')


class HelloWorld(Resource):
    def get(self):
        return {'Tarea 2': 'Taller de Integracion'}

#api.add_resource(HelloWorld, 'https://tarea2-taller.herokuapp.com/')
api.add_resource(HelloWorld, '/')

class ArtistIdAlbum(Resource):
    def get(self,artist_id):
        print("hola")
        lista = []
        lista_id = []
        lista_id_artista = []
        alb = Album.query.all()
        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artist_id}'
        for al in alb:
            lista_id.append(al.json())
        for pos in range(len(lista_id)):
            identificador = lista_id[pos]['id']
            identificador_art = lista_id[pos]['artist_id']
            nombre_pos = lista_id[pos]['name']
            genero_pos = lista_id[pos]['genre']            
            tracksurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador}/tracks'
            selfurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador}'
            lista_id_artista.append(identificador_art)
            if identificador_art == artist_id:
                lista.append({"id": identificador, "artist_id": artist_id, "name": nombre_pos, "genre": genero_pos, "artist": artisturl, "tracks": tracksurl, "self": selfurl})
        if artist_id in lista_id_artista:
            return lista
        else:
            return {'artista':'inexistente o sin albumes'},404
    
    def post(self,artist_id):
        lista = []
        lista_artista = []
        lista_id = []
        parser.add_argument('name', action='append')
        parser.add_argument('genre', action='append')
        args = parser.parse_args()
        nombre = args['name'][0]
        genero = args['genre'][0]

        #artista = Artist.query.all()
        #for art in artista:
        #    lista_artista.append(art.json())
        #for pos in range(len(lista_artista)):
        #    identificador = lista_artista[pos]['id']
        #    lista_id.append(identificador)
        #    if artist_id not in lista_id:
        #        return {"artista": "no existe"},422

        nombre_a_encriptar = nombre + ':' + artist_id
        id_encoded = b64encode(nombre_a_encriptar.encode()).decode('utf-8')[:22]        
        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artist_id}'
        tracksurl = f'https://tarea2-taller.herokuapp.com/albums/{id_encoded}/tracks'
        selfurl = f'https://tarea2-taller.herokuapp.com/albums/{id_encoded}'
        arts = Album.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            nombre_pos = lista[pos]['name']
            genero_pos = lista[pos]['genre']
            if identificador == id_encoded:
                return {"id": identificador, "artist_id": artist_id, "name": nombre_pos, "genre": genero_pos, "artist": artisturl, "tracks": tracksurl, "self": selfurl},409
        album = Album(id_encoded,artist_id,nombre,genero)
        db.session.add(album)
        db.session.commit()
        return {"id": id_encoded, "artist_id": artist_id, "name": nombre, "genre": genero, "artist": artisturl, "tracks": tracksurl, "self": selfurl},201

#api.add_resource(ArtistIdAlbum, 'https://tarea2-taller.herokuapp.com/artists/<string:artist_id>/albums')
api.add_resource(ArtistIdAlbum, '/artists/<string:artist_id>/albums')

class ArtistIdTrack(Resource):
    def get(self,artist_id):
        lista = []
        lista_final = []
        lista_artista = []
        lista_album = []
        album_artista = Album.query.all()
        trac = Track.query.all()
        for art in trac:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            album_pos = lista[pos]['album_id']
            nombre_pos = lista[pos]['name']
            duration_pos = lista[pos]['duration']
            times_pos = lista[pos]['times_played']
            albumurl = f'https://tarea2-taller.herokuapp.com/albums/{album_pos}'
            selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{identificador}'
            for alb_art in album_artista:
                lista_artista.append(alb_art.json())
            for pos in range(len(lista_artista)):
                nombre_album = lista_artista[pos]['name']
                artista_id = lista_artista[pos]['artist_id']
                nombre_encriptar = nombre_album + ':' + artista_id
                id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                if id_encode == album_pos and artista_id == artist_id: #en vez de artist_id poner un album_id
                    artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artista_id}'
                    agregar = {"id": identificador, "album_id": album_pos, "name": nombre_pos, "duration": int(duration_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl}
                    if agregar not in lista_final:
                        lista_album.append(artista_id)
                        lista_final.append({"id": identificador, "album_id": album_pos, "name": nombre_pos, "duration": int(duration_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl})
        if artist_id in lista_album:
            return lista_final
        else:
            return {'artista':'inexistente o sin canciones'},404

#api.add_resource(ArtistIdTrack, 'https://tarea2-taller.herokuapp.com/artists/<string:artist_id>/tracks')
api.add_resource(ArtistIdTrack, '/artists/<string:artist_id>/tracks')

class AlbumNames(Resource):
    def get(self):
        lista = []
        lista_id = []
        alb = Album.query.all()
        for al in alb:
            lista_id.append(al.json())
        for pos in range(len(lista_id)):
            identificador = lista_id[pos]['id']
            identificador_art = lista_id[pos]['artist_id']
            nombre_pos = lista_id[pos]['name']
            genero_pos = lista_id[pos]['genre']            
            artisturl = f'https://tarea2-taller.herokuapp.com/artists/{identificador_art}'
            tracksurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador}/tracks'
            selfurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador}'
            lista.append({"id": identificador, "artist_id": identificador_art, "name": nombre_pos, "genre": genero_pos, "artist": artisturl, "tracks": tracksurl, "self": selfurl})
        return lista
    
#api.add_resource(AlbumNames, 'https://tarea2-taller.herokuapp.com/albums')
api.add_resource(AlbumNames, '/albums')

class AlbumId(Resource):
    def get(self,Id):
        lista = []
        tracksurl = f'https://tarea2-taller.herokuapp.com/albums/{Id}/tracks'
        selfurl = f'https://tarea2-taller.herokuapp.com/albums/{Id}' 
        arts = Album.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            identificador_art = lista[pos]['artist_id']
            nombre_pos = lista[pos]['name']
            genero_pos = lista[pos]['genre']
            artisturl = f'https://tarea2-taller.herokuapp.com/artists/{identificador_art}'
            if identificador == Id:
                return {"id": identificador, "artist_id": identificador_art, "name": nombre_pos, "genre": genero_pos, "artist": artisturl, "tracks": tracksurl, "self": selfurl}
        return {'album':'inexistente'},404

    def delete(self,Id):
        lista = []
        lista_track = []
        lista_album = []
        lista_canciones = []
        albums = Album.query.all()
        for art in albums:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            nombre_album = lista[pos]['name']
            artista_id = lista[pos]['artist_id']
            nombre_encriptar = nombre_album + ':' + artista_id
            id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
            if identificador == Id:
                borrar_album = Album.query.get({'Id': identificador}) 
                tracks = Track.query.all()
                lista_album.append(Id)
                id_encoded = id_encode
                db.session.delete(borrar_album) 
        for tra in tracks:
            lista_track.append(tra.json())
        for pos in range(len(lista_track)):
            identificador_track = lista_track[pos]['id']
            alb_id = lista_track[pos]['album_id']
            if alb_id == id_encoded:
                borrar_track = Track.query.get({'Id': identificador_track}) 
                lista_canciones.append(Id)
                db.session.delete(borrar_track)
        db.session.commit()
        if Id in lista_album or Id in lista_canciones:
            return {'album':'eliminado'},204
        else:
            return {'album':'inexistente'},404        

#api.add_resource(AlbumId, 'https://tarea2-taller.herokuapp.com/albums/<string:Id>')
api.add_resource(AlbumId, '/albums/<string:Id>')

class AlbumIdTrack(Resource):
    def get(self,album_id):
        lista = []
        lista_final = []
        lista_artista = []
        lista_album = []
        album_artista = Album.query.all()
        trac = Track.query.all()
        for art in trac:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            album_pos = lista[pos]['album_id']
            nombre_pos = lista[pos]['name']
            duration_pos = lista[pos]['duration']
            times_pos = lista[pos]['times_played']
            if album_pos == album_id:
                lista_album.append(album_pos)
                albumurl = f'https://tarea2-taller.herokuapp.com/albums/{album_pos}'
                selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{identificador}'
                for alb_art in album_artista:
                    lista_artista.append(alb_art.json())
                for pos in range(len(lista_artista)):
                    nombre_id = lista_artista[pos]['name']
                    artista_id = lista_artista[pos]['artist_id']
                    nombre_encriptar = nombre_id + ':' + artista_id
                    id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                    if id_encode == album_pos:
                        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artista_id}'
                        agregar = {"id": identificador, "album_id": album_pos, "name": nombre_pos, "duration": int(duration_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl}
                        if agregar not in lista_final:
                            lista_final.append({"id": identificador, "album_id": album_pos, "name": nombre_pos, "duration": int(duration_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl})
        if album_id in lista_album:
            return lista_final
        else:
            return {'album':'inexistente o sin canciones'},404
    
    def post(self,album_id):
        lista = []
        lista_artista = []
        lista_final = []
        parser.add_argument('name', action='append')
        parser.add_argument('duration', action='append')
        args = parser.parse_args()
        nombre = args['name'][0]
        duracion = args['duration'][0]
        reproducciones = 0
        nombre_a_encriptar = nombre + ':' + album_id
        id_encoded = b64encode(nombre_a_encriptar.encode()).decode('utf-8')[:22]  
        nom_artista_id = ""      
        album_artista = Album.query.all()
        for alb_art in album_artista:
            lista_artista.append(alb_art.json())
        for pos in range(len(lista_artista)):
            nombre_id = lista_artista[pos]['name']
            artista_id = lista_artista[pos]['artist_id']
            nombre_encriptar = nombre_id + ':' + artista_id
            id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
            if id_encode == album_id:
                nom_artista_id = artista_id
        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{nom_artista_id}'
        albumurl = f'https://tarea2-taller.herokuapp.com/albums/{album_id}'
        selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{id_encoded}'
        arts = Track.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            album_pos = lista[pos]['album_id']
            nombre_pos = lista[pos]['name']
            duration_pos = lista[pos]['duration']
            times_pos = lista[pos]['times_played']
            if identificador == id_encoded:
                albumurl = f'https://tarea2-taller.herokuapp.com/albums/{album_pos}'
                selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{identificador}'
                for alb_art in album_artista:
                    lista_artista.append(alb_art.json())
                for pos in range(len(lista_artista)):
                    nombre_id = lista_artista[pos]['name']
                    artista_id = lista_artista[pos]['artist_id']
                    nombre_encriptar = nombre_id + ':' + artista_id
                    id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                    if id_encode == album_pos:
                        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artista_id}'
                        return {"id": identificador, "album_id": album_pos, "name": nombre_pos, "duration": int(duration_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl},409
        album_final = Album.query.all()
        for alb_art in album_final:
            lista_final.append(alb_art.json())
        for pos in range(len(lista_final)):
            nombre_id = lista_final[pos]['name']
            artista_id = lista_final[pos]['artist_id']
            nombre_encriptar = nombre_id + ':' + artista_id
            id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
            if id_encode == album_id:
                track = Track(id_encoded,album_id,nombre,duracion,reproducciones)
                db.session.add(track)
                db.session.commit()
                return {"id": id_encoded, "album_id": album_id, "name": nombre, "duration": int(duracion), "times_played": reproducciones, "artist": artisturl, "album": albumurl, "self": selfurl},201
        return {'album':'inexistente'},404

#api.add_resource(AlbumIdTrack, 'https://tarea2-taller.herokuapp.com/albums/<string:album_id>/tracks')
api.add_resource(AlbumIdTrack, '/albums/<string:album_id>/tracks')

class TrackNames(Resource):
    def get(self):
        lista = []
        lista_id = []
        lista_artista = []
        trac = Track.query.all()
        album_artista = Album.query.all()
        for al in trac:
            lista_id.append(al.json())
        for pos in range(len(lista_id)):
            identificador = lista_id[pos]['id']
            identificador_art = lista_id[pos]['album_id']
            nombre_pos = lista_id[pos]['name']
            duracion_pos = lista_id[pos]['duration']
            times_pos = lista_id[pos]['times_played']            
            albumurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador_art}'
            selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{identificador}'
            for alb_art in album_artista:
                lista_artista.append(alb_art.json())
            for pos in range(len(lista_artista)):
                nombre_id = lista_artista[pos]['name']
                artista_id = lista_artista[pos]['artist_id']
                nombre_encriptar = nombre_id + ':' + artista_id
                id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                if id_encode == identificador_art:
                    artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artista_id}'
            lista.append({"id": identificador, "album_id": identificador_art, "name": nombre_pos, "duration": int(duracion_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl})
        return lista
    
#api.add_resource(TrackNames, 'https://tarea2-taller.herokuapp.com/tracks')
api.add_resource(TrackNames, '/tracks')

class TrackId(Resource):
    def get(self,track_id):
        lista = []
        lista_id = []
        lista_artista = []
        lista_final = []
        trac = Track.query.all()
        album_artista = Album.query.all()
        for al in trac:
            lista_id.append(al.json())
        for pos in range(len(lista_id)):
            identificador = lista_id[pos]['id']
            identificador_art = lista_id[pos]['album_id']
            nombre_pos = lista_id[pos]['name']
            duracion_pos = lista_id[pos]['duration']
            times_pos = lista_id[pos]['times_played']            
            albumurl = f'https://tarea2-taller.herokuapp.com/albums/{identificador_art}'
            selfurl = f'https://tarea2-taller.herokuapp.com/tracks/{identificador}'
            if identificador == track_id:
                for alb_art in album_artista:
                    lista_artista.append(alb_art.json())
                for pos in range(len(lista_artista)):
                    nombre_id = lista_artista[pos]['name']
                    artista_id = lista_artista[pos]['artist_id']
                    nombre_encriptar = nombre_id + ':' + artista_id
                    id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                    if id_encode == identificador_art:
                        artisturl = f'https://tarea2-taller.herokuapp.com/artists/{artista_id}'
                        lista_final.append(identificador)
                lista.append({"id": identificador, "album_id": identificador_art, "name": nombre_pos, "duration": int(duracion_pos), "times_played": times_pos, "artist": artisturl, "album": albumurl, "self": selfurl})
        if track_id in lista_final:
            return lista
        else:
            return {'album':'inexistente o sin canciones'},404

    def delete(self,track_id):
        lista = []
        arts = Track.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            if identificador == track_id:
                borrar = Track.query.get({'Id': identificador}) 
                db.session.delete(borrar)
                db.session.commit()
                return {'album':'eliminado'},204    
        return {'album':'inexistente'},404
    
#api.add_resource(TrackId, 'https://tarea2-taller.herokuapp.com/tracks/<string:track_id>')
api.add_resource(TrackId, '/tracks/<string:track_id>')

class Play(Resource):
    def put(self,track_id):
        lista = []
        arts = Track.query.all()
        for art in arts:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            rep = lista[pos]['times_played']
            if identificador == track_id:
                cancion_suma = Track.query.get({'Id': identificador}) 
                cancion_suma.times_played += 1
                print(cancion_suma.times_played)
                db.session.add(cancion_suma)
                db.session.commit()
                return {'cancion':'reproducida'},200    
        return {'cancion':'no encontrada'},404

#api.add_resource(Play, 'https://tarea2-taller.herokuapp.com/tracks/<string:track_id>/play')
api.add_resource(Play, '/tracks/<string:track_id>/play')

class PlayAlbum(Resource):
    def put(self,album_id):
        lista = []
        lista_track = []
        lista_album = []
        album = Album.query.all()
        for art in album:
            lista.append(art.json())
        for pos in range(len(lista)):
            identificador = lista[pos]['id']
            if identificador == album_id:
                track = Track.query.all()
                for tra in track:
                    lista_track.append(tra.json())
                for posi in range(len(lista_track)):
                    identificador_track = lista_track[posi]['album_id']
                    identificador_track_id = lista_track[posi]['id']
                    if identificador_track == identificador:
                        lista_album.append(identificador)
                        cancion_suma = Track.query.get({'Id': identificador_track_id}) 
                        cancion_suma.times_played += 1
                        db.session.add(cancion_suma)
        db.session.commit()
        if album_id in lista_album:
            return {'canciones del album':'reproducidas'},200
        else:
            return {'album':'no encontrado'},404

#api.add_resource(PlayAlbum, 'https://tarea2-taller.herokuapp.com/albums/<string:album_id>/tracks/play')
api.add_resource(PlayAlbum, '/albums/<string:album_id>/tracks/play')

class PlayTrack(Resource):
    def put(self,artist_id):
        lista = []
        lista_artist = []
        lista_track = []
        lista_album = []
        lista_canciones_agregadas = []
        artista = Artist.query.all()
        for arti in artista:
            lista_artist.append(arti.json())
        for posic in range(len(lista_artist)):
            identificador_artist = lista_artist[posic]['id']
            if identificador_artist == artist_id:
                album = Album.query.all()
                for art in album:
                    lista.append(art.json())
                for pos in range(len(lista)):
                    identificador = lista[pos]['artist_id']
                    nombre = lista[pos]['name']
                    if identificador == identificador_artist:
                        nombre_encriptar = nombre + ':' + identificador
                        id_encode = b64encode(nombre_encriptar.encode()).decode('utf-8')[:22]
                        track = Track.query.all()
                        for tra in track:
                            lista_track.append(tra.json())
                        for posi in range(len(lista_track)):
                            identificador_track = lista_track[posi]['album_id']
                            identificador_track_id = lista_track[posi]['id']
                            if identificador_track == id_encode:
                                lista_album.append(identificador_artist)
                                if identificador_track_id not in lista_canciones_agregadas:
                                    lista_canciones_agregadas.append(identificador_track_id)
                                    cancion_suma = Track.query.get({'Id': identificador_track_id}) 
                                    cancion_suma.times_played += 1
                                    db.session.add(cancion_suma)
        db.session.commit()
        if artist_id in lista_album:
            return {'canciones del album':'reproducidas'},200
        else:
            return {'album':'no encontrado'},404

#api.add_resource(PlayTrack, 'https://tarea2-taller.herokuapp.com/artists/<string:artist_id>/albums/play')
api.add_resource(PlayTrack, '/artists/<string:artist_id>/albums/play')

if __name__ == '__main__':
    app.run(debug=True)
