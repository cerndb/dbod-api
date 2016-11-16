-- HOST
-- update to add the constraint in name column
CREATE TABLE public.host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT name_con UNIQUE (name)
);

