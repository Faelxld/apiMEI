package com.das.apiMEI.model;
import com.mongodb.util.JSON;
import lombok.Getter;
import lombok.Setter;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;

@Getter
@Setter
@Document(collection = "das")
public class Empresa {


    @Id
    private String _id;
    private String cnpj;
    private List<Object> das;


}

