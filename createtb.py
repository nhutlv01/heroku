from django.db import connection


class CreateTable:

    def __init__(self):
        self.cursor = connection.cursor()

    def create(self):
        #Create table user on public schema
        #Talbe ----users----
        self.cursor.execute("CREATE TABLE users\
                            (\
	                            id bigserial NOT NULL PRIMARY KEY,\
	                            username varchar(30) NOT NULL UNIQUE,\
	                            password varchar NOT NULL,\
	                            email varchar NOT NULL UNIQUE,\
	                            full_name varchar(30),\
	                            sex varchar(6),\
	                            profile_picture varchar,\
	                            create_time bigint\
                            );")


        #--Table ----follows----
        self.cursor.execute("CREATE TABLE follows\
                            (\
	                            user_id bigint NOT NULL REFERENCES users(id),\
	                            target_id bigint NOT NULL REFERENCES users(id),\
	                            PRIMARY KEY(user_id, target_id)\
                            );")


        for i in range(0, 200):
            #create 2000
            self.cursor.execute("CREATE SCHEMA test%s" %i)


            #Create sequence
            self.cursor.execute("CREATE SEQUENCE test%s.table_id_seq START 1;" %i)


            #Create function to auto generate ID
            self.cursor.execute("CREATE OR REPLACE FUNCTION test%s.next_id(OUT result bigint) AS $$\
                                DECLARE\
                                    our_epoch bigint := 1314220021721;\
                                    seq_id bigint;                                    now_millis bigint;\
                                    shard_id int := %d;\
                                BEGIN\
                                SELECT nextval('test%s.table_id_seq') %% 1024 INTO seq_id;\
                                SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;\
                                result := (now_millis - our_epoch) << 23;\
                                result := result | (shard_id << 10);\
                                result := result | (seq_id);\
                                END;\
                                $$ LANGUAGE PLPGSQL;" %(i, i, i))


            #Create table photos, comments, likes, follows, feeds on each schema
            #Table ----photos----
            self.cursor.execute("CREATE TABLE test%s.photos\
                                (\
	                                id bigint NOT NULL PRIMARY KEY DEFAULT test%s.next_id(),\
	                                user_id bigint NOT NULL REFERENCES users(id),\
	                                caption text,\
	                                low_resolution varchar,\
	                                hight_resolution varchar,\
	                                thumnail varchar,\
	                                create_time bigint\
                                );" %(i, i))

            #Table ----comments----
            self.cursor.execute("CREATE TABLE test%s.comments\
                                (\
	                                id bigint NOT NULL PRIMARY KEY DEFAULT test%s.next_id(),\
	                                user_id bigint REFERENCES users(id),\
	                                photo_id bigint REFERENCES test%s.photos(id),\
	                                text varchar,\
                                    create_time bigint\
                                );" %(i, i, i))


            #--Table ----likes----
            self.cursor.execute("CREATE TABLE test%s.likes\
                                (\
                                    user_id bigint REFERENCES users(id),\
	                                photo_id bigint REFERENCES test%s.photos(id),\
	                                PRIMARY KEY(photo_id, user_id)\
                                );" %(i, i))



            #--Table ----feeds----
            self.cursor.execute("CREATE TABLE test%s.feeds\
                                (\
	                                user_id bigint NOT NULL REFERENCES users(id),\
	                                photo_id bigint NOT NULL ,\
	                                PRIMARY KEY(user_id, photo_id)\
                                );" %(i))
            #Index for feeds
            self.cursor.execute("CREATE INDEX user_index ON test%s.feeds (user_id);" %(i))

    def __del__(self):
        self.cursor.close()