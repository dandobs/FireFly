create table image_records (
	recordID 		int NOT NULL AUTO_INCREMENT,
    locID			int NOT NULL,
    date_time		datetime,
    irImagePath		varchar(1024),
    rgbImagePath	varchar(1024),
    primary key (recordID)
    );

create table locations (
    locID			int NOT NULL AUTO_INCREMENT,
    lon            	float,
    lat				float,
    primary key (locID)
    );
    
create table hotspots (
	hotspotID 		int NOT NULL AUTO_INCREMENT,
    locID			int NOT NULL,
    size			int,
    hotspot_status	int,
    primary key (hotspotID)
    );

create table fire_dep_areas (
	areaID 			int NOT NULL AUTO_INCREMENT,
    depID			int,
	bottomLeftX		float,
    bottomLeftY		float,
    topRightX		float,
    topRightY		float,    
    primary key (areaID)
    );
    
ALTER TABLE image_records ADD FOREIGN KEY (locID) REFERENCES locations(locID);
ALTER TABLE hotspots ADD FOREIGN KEY (locID) REFERENCES locations(locID);
