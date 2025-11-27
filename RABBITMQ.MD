# RabbitMQ

## Enable MQTT plugin

Update the configmap `rabbitmq-<env>-rabbitmq-config` in the installation manifest to include `rabbitmq_mqtt` in the `enabled_plugins`:

```conf
      [rabbitmq_management,rabbitmq_peer_discovery_k8s,rabbitmq_prometheus,rabbitmq_mqtt].
```

## Updating Root CA

RabbitMQ certificates are handled by cert-manager. The ACME issuer doesn't return the root certificate authority (required by rabbitmq), so we must fetch it ourselves and insert it into `rabbitmq-cert.yaml`. If using Let's Encrypt, you can fetch the relevant root CA with:

```shell
curl -s https://letsencrypt.org/certs/isrgrootx1.pem
```

The current CA is valid until `Jun 4 11:04:38 2035 GMT`


## Enabling TLS

Update the configmap with the following configurations:

`rabbit.conf`:
```conf
      # Enable MQTTS
      mqtt.listeners.ssl.default        = 8883
      ssl_options.cacertfile            = /etc/rabbitmq/ca/ca.crt
      ssl_options.certfile              = /etc/rabbitmq/certs/tls.crt
      ssl_options.keyfile               = /etc/rabbitmq/certs/tls.key
      ssl_options.verify                = verify_none
      ssl_options.fail_if_no_peer_cert  = false
      # Disable TCP without TLS
      listeners.tcp = none
```

## Disabling unnecessary ports

Remove unnecessary ports from services `rabbitmq-${ENV}-rabbitmq-discovery` and `rabbitmq-${ENV}-rabbitmq-svc`

```conf
spec:
  ports:
  - name: clustering
    port: 25672
  - name: prometheus
    port: 15692
  - name: mqtts
    port: 8883
  - name: http
    port: 15672
```

## Mounting certificates

in volumes:
```yaml
      - name: mqtts-certs
        secret:
          secretName: rabbitmq-${ENV}-mqtt-cert-secret
      - name: root-ca
        configMap:
          name: rabbitmq-${ENV}-ca
          items:
            - key: ca.crt
              path: ca.crt
```

in volumeMounts:
```yaml
        - name: mqtts-certs
          mountPath: /etc/rabbitmq/certs
          readOnly: true
        - name: root-ca
          mountPath: /etc/rabbitmq/ca
          readOnly: true
```
