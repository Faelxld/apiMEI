package com.das.apiMEI.repository;

import com.das.apiMEI.model.Empresa;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface EmpresaRepository extends MongoRepository<Empresa, String> {
    Empresa findBy_id(String cnpj);
}